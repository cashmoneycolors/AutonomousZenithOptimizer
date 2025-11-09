namespace ZenithCoreSystem.Core
{
    public class OptimizerSettings
    {
        public int QmlRetryCount { get; set; } = 3;

        public int QmlBaseDelayMilliseconds { get; set; } = 500;

        public double ComplianceThreshold { get; set; } = 0.9;

        public bool SimulateQmlFailure { get; set; } = true;

        public string? RedisConnectionString { get; set; }
    }
}
