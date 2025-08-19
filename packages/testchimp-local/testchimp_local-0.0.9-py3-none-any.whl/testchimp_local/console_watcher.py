import time
from typing import List
from playwright.async_api import BrowserContext
from .datas import ConsoleLogEntry

class ConsoleWatcher:
    MAX_LOGS = 100

    def __init__(self, context: BrowserContext):
        self.context = context
        self.console_logs: List[ConsoleLogEntry] = []

    async def start(self):
        # Expose a binding to receive logs from the browser context
        await self.context.expose_binding("sendConsoleLogToPython", self._handle_console_log)

        # Inject the logging script
        await self.context.add_init_script(script="""
            (function () {
                const sendLog = (type, args) => {
                    const text = args.map(a => {
                        try { return typeof a === 'string' ? a : JSON.stringify(a); }
                        catch { return String(a); }
                    }).join(' ');

                    if (window.sendConsoleLogToPython) {
                        window.sendConsoleLogToPython({ type, text, timestamp: Date.now() });
                    }
                };

                const originalError = console.error;
                const originalWarn = console.warn;

                console.error = function (...args) {
                    sendLog('error', args);
                    originalError.apply(console, args);
                };

                console.warn = function (...args) {
                    sendLog('warning', args);
                    originalWarn.apply(console, args);
                };                                         
            })();
        """)

    async def _handle_console_log(self, source, payload):
        entry = ConsoleLogEntry(**payload)
        self.console_logs.append(entry)
        if len(self.console_logs) > self.MAX_LOGS:
            self.console_logs = self.console_logs[-self.MAX_LOGS:]  # keep only the last 100

    def get_console_logs_since(self, timestamp: int) -> List[ConsoleLogEntry]:
        return [log for log in self.console_logs if log.timestamp >= timestamp]