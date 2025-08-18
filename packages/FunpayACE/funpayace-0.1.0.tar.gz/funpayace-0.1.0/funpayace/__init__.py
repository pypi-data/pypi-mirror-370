from __future__ import annotations

import asyncio
import logging
import random
import re
import threading
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, Coroutine, Set

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector, CookieJar
from bs4 import BeautifulSoup
from yarl import URL

__all__ = [
    "FunpayAce",
    "FunpayAceError",
    "RequestError",
    "BalanceParseError",
    "FunpayConfig",
]

# ---------------------------------------------------------------------
# ЛОГИРОВАНИЕ
# ---------------------------------------------------------------------
logger = logging.getLogger("FunpayACE")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())  # библиотека не должна перенастраивать логи


# ---------------------------------------------------------------------
# ИСКЛЮЧЕНИЯ
# ---------------------------------------------------------------------
class FunpayAceError(Exception):
    """Базовое исключение библиотеки."""


class RequestError(FunpayAceError):
    """Исключение для ошибок HTTP/сетевых операций."""


class BalanceParseError(FunpayAceError):
    """Исключение, если не удалось корректно распарсить баланс."""


# ---------------------------------------------------------------------
# КОНФИГ
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class FunpayConfig:
    """
    Конфигурация клиента.
    """
    base_url: str = "https://funpay.com"
    # Реалистичный браузерный UA — снижает шанс блокировок WAF/CDN
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    # Таймаут запроса (сек)
    request_timeout: float = 20.0
    # Ограничение одновременных соединений
    connector_limit: int = 10
    # Ретраи с экспоненциальным бэк-оффом
    max_retries: int = 4
    backoff_base: float = 0.75
    backoff_max: float = 8.0
    # Интервалы между циклами (джиттер)
    ping_interval_min: float = 45.0
    ping_interval_max: float = 100.0
    raise_interval_min: float = 60.0
    raise_interval_max: float = 300.0
    # SSL
    ssl: bool = True
    # Дублировать Cookie в заголовке (страховка)
    send_cookie_header_always: bool = True
    # Диагностика авторизации (лог текущих cookies и csrf)
    debug_auth: bool = False


# ---------------------------------------------------------------------
# УТИЛИТЫ
# ---------------------------------------------------------------------
def _jitter(min_s: float, max_s: float) -> float:
    """Случайная пауза с равномерным распределением."""
    return random.uniform(min_s, max_s)


async def _retry_with_backoff(
    op: Callable[[], Coroutine[Any, Any, aiohttp.ClientResponse]],
    *,
    max_retries: int,
    base: float,
    max_sleep: float,
    retry_for_status: Set[int] = frozenset({429, 500, 502, 503, 504}),
) -> aiohttp.ClientResponse:
    """
    Универсальный ретрай с экспоненциальным бэк-оффом и джиттером.
    Возвращает успешный (status < 400) ответ или бросает RequestError.
    """
    attempt = 0
    while True:
        try:
            resp = await op()
            if resp.status < 400:
                return resp

            if resp.status in retry_for_status and attempt < max_retries:
                attempt += 1
                delay = min(max_sleep, base * (2 ** (attempt - 1))) + random.uniform(0, base)
                logger.warning("HTTP %s, retry %s/%s in %.2fs", resp.status, attempt, max_retries, delay)
                await asyncio.sleep(delay)
                continue

            text = await resp.text()
            raise RequestError(f"HTTP {resp.status}: {text[:200]}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < max_retries:
                attempt += 1
                delay = min(max_sleep, base * (2 ** (attempt - 1))) + random.uniform(0, base)
                logger.warning("Network error %r, retry %s/%s in %.2fs", e, attempt, max_retries, delay)
                await asyncio.sleep(delay)
                continue
            raise RequestError(f"Network error after {max_retries} retries: {e}") from e


# ---------------------------------------------------------------------
# КЛИЕНТ
# ---------------------------------------------------------------------
@dataclass
class FunpayAce:
    """
    Асинхронный клиент Funpay.

    Возможности:
    - forever_online: поддержание «онлайна» пингами POST /runner/
    - lot_auto_boost: автоподнятие лотов POST /lots/raise
    - get_balance: парсинг балансов со страницы /account/balance
    """
    golden_key: str
    config: FunpayConfig = field(default_factory=FunpayConfig)

    _session: Optional[ClientSession] = field(init=False, default=None)
    _tasks: Set[asyncio.Task] = field(init=False, default_factory=set)
    _csrf: Optional[str] = field(init=False, default=None)
    _warmed_up: bool = field(init=False, default=False)

    # -------------------- session lifecycle --------------------
    async def _ensure_session(self) -> ClientSession:
        """
        Создаёт и/или возвращает живую сессию. Явно привязываем cookie к домену.
        """
        if self._session and not self._session.closed:
            return self._session

        timeout = ClientTimeout(total=self.config.request_timeout)
        headers = {
            "User-Agent": self.config.user_agent,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": f"{self.config.base_url}/",
            "Origin": self.config.base_url,
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        connector = TCPConnector(limit=self.config.connector_limit, ssl=self.config.ssl)

        # Привязываем golden_key к домену
        jar = CookieJar(unsafe=True)
        jar.update_cookies({"golden_key": self.golden_key}, URL(self.config.base_url))

        self._session = aiohttp.ClientSession(
            base_url=self.config.base_url,
            timeout=timeout,
            connector=connector,
            headers=headers,
            cookie_jar=jar,
        )
        self._csrf = None
        self._warmed_up = False
        return self._session

    async def aclose(self) -> None:
        """Останавливает фоновые задачи и закрывает HTTP-сессию."""
        await self.cancel_background_tasks()
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._csrf = None
        self._warmed_up = False

    async def __aenter__(self) -> "FunpayAce":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    @asynccontextmanager
    async def session(self) -> ClientSession:
        """Контекстный менеджер для точечного использования сессии."""
        sess = await self._ensure_session()
        try:
            yield sess
        finally:
            pass

    # -------------------- auth warm-up & headers --------------------
    def _with_cookie_header(
        self,
        extra: Dict[str, str] | None = None,
        *,
        include_csrf: bool = True,
    ) -> Dict[str, str]:
        """
        Возвращает headers c дублированием `Cookie: golden_key=...` (страховка) и X-CSRF-Token (если есть).
        """
        headers: Dict[str, str] = {}
        if self.config.send_cookie_header_always:
            headers["Cookie"] = f"golden_key={self.golden_key};"
        if include_csrf and self._csrf:
            headers["X-CSRF-Token"] = self._csrf
        if extra:
            headers.update(extra)
        return headers

    async def _warm_up(self) -> None:
        """
        Первичный заход, чтобы:
          • сервер проставил служебные куки (если нужно),
          • вытащить CSRF-токен (если присутствует).
        """
        if self._warmed_up:
            return

        async with self.session() as sess:
            # 1) GET /
            resp = await _retry_with_backoff(
                lambda: sess.get("/", headers=self._with_cookie_header(include_csrf=False)),
                max_retries=self.config.max_retries,
                base=self.config.backoff_base,
                max_sleep=self.config.backoff_max,
            )
            html = await resp.text()
            self._csrf = self._extract_csrf(html) or self._csrf

            # 2) GET /account — иногда тут есть CSRF
            try:
                resp2 = await _retry_with_backoff(
                    lambda: sess.get("/account", headers=self._with_cookie_header(include_csrf=False)),
                    max_retries=self.config.max_retries,
                    base=self.config.backoff_base,
                    max_sleep=self.config.backoff_max,
                )
                html2 = await resp2.text()
                self._csrf = self._extract_csrf(html2) or self._csrf
            except RequestError:
                pass

            if self.config.debug_auth:
                dom = URL(self.config.base_url)
                seen = sess.cookie_jar.filter_cookies(dom)
                logger.info("Auth debug: cookies for %s -> %s", dom.host, {k: v.value for k, v in seen.items()})
                logger.info("Auth debug: csrf -> %r", self._csrf)

            self._warmed_up = True

    @staticmethod
    def _extract_csrf(html: str) -> Optional[str]:
        """
        Пытаемся найти CSRF в популярных форматах:
          - <meta name="csrf-token" content="...">
          - <input type="hidden" name="csrf" value="...">
          - <input type="hidden" name="csrf_token" value="...">
          - <input type="hidden" name="_csrf" value="..."> и т.п.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            meta = soup.find("meta", attrs={"name": "csrf-token"})
            if meta and meta.get("content"):
                return meta.get("content").strip()
            for name in ("csrf", "csrf_token", "_csrf", "_token"):
                inp = soup.find("input", attrs={"name": name})
                if inp and inp.get("value"):
                    return inp.get("value").strip()
        except Exception:
            pass
        return None

    # -------------------- background tasks helpers --------------------
    def _track_task(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
        """Создаёт фоновую задачу и трекает её для корректной отмены."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def cancel_background_tasks(self) -> None:
        """Корректно отменяет все фоновые задачи клиента."""
        if not self._tasks:
            return
        for t in list(self._tasks):
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    # -------------------- public async APIs --------------------
    async def forever_online(self) -> None:
        """Бесконечно поддерживает «онлайн» пингами `/runner/`."""
        async with self.session() as sess:
            await self._warm_up()
            logger.info("Вечный онлайн запущен.")
            while True:
                try:
                    resp = await _retry_with_backoff(
                        lambda: sess.post("/runner/", headers=self._with_cookie_header()),
                        max_retries=self.config.max_retries,
                        base=self.config.backoff_base,
                        max_sleep=self.config.backoff_max,
                    )
                    if resp.status == 200:
                        logger.debug("Ping OK.")
                    else:
                        logger.warning("Ping: HTTP %s", resp.status)
                except asyncio.CancelledError:
                    logger.info("forever_online: canceled")
                    raise
                except Exception as e:
                    logger.exception("Ошибка при ping: %s", e)

                await asyncio.sleep(_jitter(self.config.ping_interval_min, self.config.ping_interval_max))

    async def lot_auto_boost(self, game_id: int, node_id: int) -> None:
        """Бесконечно поднимает лоты запросами `/lots/raise`."""
        async with self.session() as sess:
            await self._warm_up()
            logger.info("Автоподнятие запущено (game_id=%s, node_id=%s).", game_id, node_id)

            form = aiohttp.FormData()
            form.add_field("game_id", str(game_id))
            form.add_field("node_id", str(node_id))
            # На всякий случай — если сервер ожидает csrf в форме:
            if self._csrf:
                form.add_field("csrf", self._csrf)

            while True:
                try:
                    resp = await _retry_with_backoff(
                        lambda: sess.post("/lots/raise", data=form, headers=self._with_cookie_header()),
                        max_retries=self.config.max_retries,
                        base=self.config.backoff_base,
                        max_sleep=self.config.backoff_max,
                    )
                    try:
                        payload: Dict[str, Any] = await resp.json(content_type=None)
                    except Exception:
                        text = await resp.text()
                        payload = {"msg": text[:200]}
                    logger.info("Ответ сервера: %s", payload.get("msg", "OK"))
                except asyncio.CancelledError:
                    logger.info("lot_auto_boost: canceled")
                    raise
                except Exception as e:
                    logger.exception("Ошибка при автоподнятии: %s", e)

                await asyncio.sleep(_jitter(self.config.raise_interval_min, self.config.raise_interval_max))

    async def get_balance(self) -> Dict[str, float]:
        """
        Возвращает словарь балансов, напр. {"RUB": 123.45, "USD": 12.34, "EUR": 5.67}.

        Метод устойчив к разной вёрстке:
        - ищет значения в известных блоках;
        - парсит по тексту с валютами/символами (RUB/USD/EUR/₽/$/€);
        - пытается вытащить из встроенного JSON внутри <script>.
        """
        async with self.session() as sess:
            await self._warm_up()
            resp = await _retry_with_backoff(
                lambda: sess.get("/account/balance", headers=self._with_cookie_header()),
                max_retries=self.config.max_retries,
                base=self.config.backoff_base,
                max_sleep=self.config.backoff_max,
            )

            ctype = resp.headers.get("Content-Type", "")
            text = await resp.text()

            # Если пришёл JSON — пробуем вытащить напрямую
            if "application/json" in ctype.lower():
                import json
                try:
                    data = json.loads(text)
                    for key in ("balances", "data", "result"):
                        if isinstance(data, dict) and isinstance(data.get(key), dict):
                            parsed: Dict[str, float] = {}
                            for cur, val in data[key].items():
                                try:
                                    parsed[cur.upper()] = float(str(val).replace(" ", "").replace(",", "."))
                                except Exception:
                                    pass
                            if parsed:
                                preferred = ("RUB", "USD", "EUR")
                                filtered = {k: v for k, v in parsed.items() if k in preferred}
                                return filtered or parsed
                except Exception:
                    pass  # упадём в HTML-парсер ниже

            # HTML путь
            html = text
            balances = self._parse_balances_from_html(html)
            if balances:
                preferred = ("RUB", "USD", "EUR")
                filtered = {k: v for k, v in balances.items() if k in preferred}
                return filtered or balances

            # Диагностика: покажем немного контента, чтобы понять разметку
            snippet = re.sub(r"\s+", " ", html)[:300]
            logger.error("Не удалось распарсить баланс. Первые 300 символов страницы: %r", snippet)
            raise BalanceParseError("Не удалось распарсить значения балансов.")

    @staticmethod
    def _parse_balances_from_html(html: str) -> Dict[str, float]:
        """
        Пытается вытащить балансы из HTML разными способами:
          1) Ищет известные контейнеры и элементы.
          2) Сканирует по тексту пары валюта+число (в т.ч. символы ₽/$/€).
          3) Пытается достать значения из JSON-вкраплений <script>...</script>.
        Возвращает словарь {'RUB': 123.45, ...} или {}.
        """
        soup = BeautifulSoup(html, "html.parser")
        text_all = soup.get_text(" ", strip=True).replace("\xa0", " ")

        balances: Dict[str, float] = {}
        num = r"([\d\s\u00A0.,]+)"  # учитываем неразрывные пробелы
        cur_codes = r"(RUB|USD|EUR)"
        cur_syms = r"(₽|\$|€)"
        sep = r"[:=\-–—]?"
        ws = r"\s*"

        def to_float(s: str) -> Optional[float]:
            s = s.replace("\xa0", " ").replace(" ", "").replace(",", ".")
            try:
                return float(s)
            except ValueError:
                return None

        # 1) Известные блоки / элементы
        container = soup.select_one(".balances-list") or soup.select_one("#balances") or soup
        candidates = container.select(".balances-item, .balances-value, span, div, li, td")
        for node in candidates:
            t = node.get_text(" ", strip=True)
            if not t:
                continue
            # “RUB 1 234,56” или “1 234,56 RUB”
            m1 = re.search(fr"{cur_codes}{ws}{sep}{ws}{num}", t, re.IGNORECASE)
            m2 = re.search(fr"{num}{ws}{sep}{ws}{cur_codes}", t, re.IGNORECASE)
            # Символы валют
            m3 = re.search(fr"{cur_syms}{ws}{sep}{ws}{num}", t)
            m4 = re.search(fr"{num}{ws}{sep}{ws}{cur_syms}", t)

            if m1:
                code, val = m1.group(1).upper(), m1.group(2)
                f = to_float(val)
                if f is not None:
                    balances[code] = f
            if m2:
                val, code = m2.group(1), m2.group(2).upper()
                f = to_float(val)
                if f is not None:
                    balances[code] = f
            if m3:
                sym, val = m3.group(1), m3.group(2)
                f = to_float(val)
                if f is not None:
                    if sym == "₽":
                        balances["RUB"] = f
                    elif sym == "$":
                        balances["USD"] = f
                    elif sym == "€":
                        balances["EUR"] = f
            if m4:
                val, sym = m4.group(1), m4.group(2)
                f = to_float(val)
                if f is not None:
                    if sym == "₽":
                        balances["RUB"] = f
                    elif sym == "$":
                        balances["USD"] = f
                    elif sym == "€":
                        balances["EUR"] = f

        # 2) По всему тексту страницы
        if not balances:
            for m in re.finditer(fr"{cur_codes}{ws}{sep}{ws}{num}", text_all, re.IGNORECASE):
                code, val = m.group(1).upper(), m.group(2)
                f = to_float(val)
                if f is not None:
                    balances[code] = f
            for m in re.finditer(fr"{num}{ws}{sep}{ws}{cur_codes}", text_all, re.IGNORECASE):
                val, code = m.group(1), m.group(2).upper()
                f = to_float(val)
                if f is not None:
                    balances[code] = f
            for m in re.finditer(fr"{cur_syms}{ws}{sep}{ws}{num}", text_all):
                sym, val = m.group(1), m.group(2)
                f = to_float(val)
                if f is not None:
                    if sym == "₽":
                        balances["RUB"] = f
                    elif sym == "$":
                        balances["USD"] = f
                    elif sym == "€":
                        balances["EUR"] = f
            for m in re.finditer(fr"{num}{ws}{sep}{ws}{cur_syms}", text_all):
                val, sym = m.group(1), m.group(2)
                f = to_float(val)
                if f is not None:
                    if sym == "₽":
                        balances["RUB"] = f
                    elif sym == "$":
                        balances["USD"] = f
                    elif sym == "€":
                        balances["EUR"] = f

        # 3) Встроенные JSON-скрипты
        if not balances:
            scripts = soup.find_all("script")
            jrx = re.compile(r'"(RUB|USD|EUR)"\s*:\s*"?(?P<val>[\d\s\u00A0.,]+)"?', re.IGNORECASE)
            for sc in scripts:
                s = sc.string or sc.get_text() or ""
                for m in jrx.finditer(s):
                    code = m.group(1).upper()
                    f = to_float(m.group("val"))
                    if f is not None:
                        balances[code] = f

        return balances

    # -------------------- convenience runners --------------------
    def start_forever_online_task(self) -> asyncio.Task:
        """Запускает `forever_online()` как фоновую задачу в текущем event loop."""
        return self._track_task(self.forever_online())

    def start_lot_auto_boost_task(self, game_id: int, node_id: int) -> asyncio.Task:
        """Запускает `lot_auto_boost()` как фоновую задачу в текущем event loop."""
        return self._track_task(self.lot_auto_boost(game_id, node_id))

    def run_forever_online_in_thread(self) -> threading.Thread:
        """Запуск `forever_online()` в отдельной нити с приватным event loop."""
        return _run_coro_in_thread(self._thread_entry(self.forever_online))

    def run_lot_auto_boost_in_thread(self, game_id: int, node_id: int) -> threading.Thread:
        """Запуск `lot_auto_boost()` в отдельной нити с приватным event loop."""
        return _run_coro_in_thread(self._thread_entry(lambda: self.lot_auto_boost(game_id, node_id)))

    async def _thread_entry(self, factory: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """Приватный вход в корутину для нитевого запуска: создаёт сессию и корректно её закрывает."""
        async with self:
            await factory()


# ---------------------------------------------------------------------
# НИТЕВОЙ РАННЕР
# ---------------------------------------------------------------------
def _run_coro_in_thread(coro: Coroutine[Any, Any, None]) -> threading.Thread:
    """
    Создаёт отдельную демонизированную нить с собственным event loop,
    запускает корутину до отмены и аккуратно закрывает loop при завершении.
    """
    def _runner() -> None:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
        finally:
            pending = asyncio.all_tasks(loop)
            for t in pending:
                t.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    t = threading.Thread(target=_runner, daemon=True, name="FunpayACE-Thread")
    t.start()
    return t
