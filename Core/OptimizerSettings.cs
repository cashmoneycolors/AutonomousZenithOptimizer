namespace ZenithCoreSystem.Core
{
    public class OptimizerSettings
    {
        public int QmlRetryCount { get; set; } = 3;
        public int QmlBaseDelayMilliseconds { get; set; } = 500;
        public double ComplianceThreshold { get; set; } = 0.9;

        /// <summary>
        /// Aktiviert echten Live-Betrieb. In LiveMode sind Demo-Pfade deaktiviert und es werden Guardrails erzwungen.
        /// </summary>
        public bool LiveMode { get; set; } = false;

        /// <summary>
        /// Simuliert QML-Ausfälle (nur für Tests/Entwicklung). In LiveMode muss dies false sein.
        /// </summary>
        public bool SimulateQmlFailure { get; set; } = false;

        /// <summary>
        /// QML HTTP Endpoint, z.B. http://localhost:8501/api/qml_decision
        /// In LiveMode muss das gesetzt sein (per ENV oder Config).
        /// </summary>
        public string? QmlEndpoint { get; set; }

        /// <summary>
        /// Redis Connection String (Secrets bitte via ENV/Secret Store).
        /// </summary>
        public string? RedisConnectionString { get; set; }


        /// <summary>
        /// Aktiviert Demo-Szenarien (Order-Tests). In LiveMode muss das false sein.
        /// </summary>
        public bool EnableDemoScenarios { get; set; } = false;

        /// <summary>
        /// Wartezeit zwischen Zyklen in Sekunden (Standard: 60s).
        /// </summary>
        public int CycleDelaySeconds { get; set; } = 60;

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
    }
}
