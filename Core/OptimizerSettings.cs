namespace ZenithCoreSystem.Core
{
    public class OptimizerSettings
    {
        public int QmlRetryCount { get; set; } = 3;

        public int QmlBaseDelayMilliseconds { get; set; } = 500;

        public double ComplianceThreshold { get; set; } = 0.9;

        public bool SimulateQmlFailure { get; set; } = true;

        public string? RedisConnectionString { get; set; }

        /// <summary>
        /// Aktiviert Demo-Szenarien (Order-Tests). In Produktion auf false setzen.
        /// </summary>
        public bool EnableDemoScenarios { get; set; } = true;

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
