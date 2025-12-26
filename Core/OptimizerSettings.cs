namespace ZenithCoreSystem.Core
{
    public class OptimizerSettings
    {
        /// <summary>
        /// Anzahl Retry-Versuche (pro Zyklus) für QML Decision.
        /// </summary>
        public int QmlRetryCount { get; set; } = 3;

        public int QmlBaseDelayMilliseconds { get; set; } = 500;

        public double ComplianceThreshold { get; set; } = 0.9;

        public bool SimulateQmlFailure { get; set; } = false;

        public string? RedisConnectionString { get; set; } = Environment.GetEnvironmentVariable("REDIS_CONNECTION_STRING");

        /// <summary>
        /// Aktiviert Demo-Szenarien (Order-Tests). In Produktion auf false setzen.
        /// </summary>
        public bool EnableDemoScenarios { get; set; } = true;

        /// <summary>
        /// Wartezeit zwischen Zyklen in Sekunden (Standard: 60s).
        /// </summary>
        public int CycleDelaySeconds { get; set; } = 60;

        /// <summary>
        /// Maximale Anzahl aufeinanderfolgender Fehler im Hauptloop, bevor ein Cooldown erzwungen wird.
        /// (Kein Shutdown; 24/7 Betrieb.)
        /// </summary>
        public int MaxConsecutiveErrors { get; set; } = 5;

        /// <summary>
        /// Cooldown-Dauer in Sekunden nach MaxConsecutiveErrors.
        /// </summary>
        public int ErrorCooldownSeconds { get; set; } = 300;

        /// <summary>
        /// Maximaler Backoff in Sekunden zwischen Retries im Hauptloop.
        /// </summary>
        public int ErrorBackoffMaxSeconds { get; set; } = 300;

        /// <summary>
        /// Jitter-Spanne (in Millisekunden), die auf Backoff/Cooldown addiert wird.
        /// Reduziert Thundering-Herd / Timing-Korrelation.
        /// </summary>
        public int ErrorJitterMaxMilliseconds { get; set; } = 1000;

        /// <summary>
        /// Wenn true, wird pro Zyklus das große Konsolen-Dashboard ausgegeben.
        /// Bei 24/7 Betrieb oft sinnvoll: false (spart CPU/IO).
        /// </summary>
        public bool EnableConsoleDashboard { get; set; } = true;

        /// <summary>
        /// Basisbetrag für Trades vor Scale-Up-Faktor.
        /// </summary>
        public decimal BaseTradeAmount { get; set; } = 100000.00m;

        /// <summary>
        /// Minimal erlaubter SCALE_UP-Faktor (z. B. 1.0).
        /// </summary>
        public decimal ScaleUpMinFactor { get; set; } = 1.0m;

        /// <summary>
        /// Maximal erlaubter SCALE_UP-Faktor ("Quantum-Stufe").
        /// </summary>
        public decimal ScaleUpMaxFactor { get; set; } = 3.0m;

        /// <summary>
        /// QML Endpoint URL.
        /// </summary>
        public string? QmlEndpoint { get; set; }

        /// <summary>
        /// Live Mode aktivieren.
        /// </summary>
        public bool LiveMode { get; set; } = false;
    }
}