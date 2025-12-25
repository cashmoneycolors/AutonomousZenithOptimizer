namespace ZenithCoreSystem.Core
{
    public class OptimizerSettings
    {
        public int QmlRetryCount { get; set; } = 3;

        public int QmlBaseDelayMilliseconds { get; set; } = 500;

        public double ComplianceThreshold { get; set; } = 0.9;

        public bool SimulateQmlFailure { get; set; } = true;

        public string? RedisConnectionString { get; set; }

        // Mining Optimization Service Settings
        public bool EnableMiningOptimization { get; set; } = false;

        public int MiningOptimizationIntervalSeconds { get; set; } = 300; // 5 Minuten Standard

        public string PythonExecutablePath { get; set; } = "python"; // Default Python executable
        
        // Advanced AI Service Settings
        public bool EnableAdvancedAI { get; set; } = false;
        
        public int AIAnalysisIntervalSeconds { get; set; } = 180; // 3 Minuten Standard
    }
}
