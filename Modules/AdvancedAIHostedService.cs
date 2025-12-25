using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Diagnostics;
using System.Text.Json;
using ZenithCoreSystem.Core;
using ZenithCoreSystem.Modules;

namespace ZenithCoreSystem.Modules;

/// <summary>
/// Advanced AI integration service for quantum optimization, neural trading, and predictive analytics
/// </summary>
public class AdvancedAIHostedService : BackgroundService
{
    private readonly ILogger<AdvancedAIHostedService> _logger;
    private readonly OptimizerSettings _settings;
    private readonly IConnectionMultiplexer _cache;
    private readonly TimeSpan _interval;

    public AdvancedAIHostedService(
        ILogger<AdvancedAIHostedService> logger,
        IOptions<OptimizerSettings> settings,
        IConnectionMultiplexer cache)
    {
        _logger = logger;
        _settings = settings.Value;
        _cache = cache;
        _interval = TimeSpan.FromSeconds(_settings.AIAnalysisIntervalSeconds);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (!_settings.EnableAdvancedAI)
        {
            _logger.LogInformation("[AdvancedAI] Advanced AI features disabled in configuration");
            return;
        }

        _logger.LogInformation("[AdvancedAI] Advanced AI Service started");
        _logger.LogInformation("[AdvancedAI] Analysis interval: {Interval} seconds", _settings.AIAnalysisIntervalSeconds);

        await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken); // Initial delay

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await RunAdvancedAIAnalysisAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "[AdvancedAI] Error during AI analysis cycle");
            }

            await Task.Delay(_interval, stoppingToken);
        }

        _logger.LogInformation("[AdvancedAI] Advanced AI Service stopped");
    }

    private async Task RunAdvancedAIAnalysisAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("[AdvancedAI] Starting advanced AI analysis cycle...");

        var scriptPath = Path.Combine("python_modules", "advanced_ai_coordinator.py");
        
        if (!File.Exists(scriptPath))
        {
            _logger.LogWarning("[AdvancedAI] Script not found: {ScriptPath}", scriptPath);
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = _settings.PythonExecutablePath,
            Arguments = $"\"{scriptPath}\"",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = new Process { StartInfo = startInfo };
        
        process.Start();
        
        var output = await process.StandardOutput.ReadToEndAsync(cancellationToken);
        var errors = await process.StandardError.ReadToEndAsync(cancellationToken);

        await process.WaitForExitAsync(cancellationToken);

        if (process.ExitCode != 0)
        {
            _logger.LogWarning("[AdvancedAI] Script exited with code {ExitCode}. Error: {Error}", 
                process.ExitCode, errors);
            return;
        }

        // Parse and cache AI analysis results
        try
        {
            var result = JsonSerializer.Deserialize<AdvancedAIResult>(output);
            if (result != null)
            {
                await CacheAIResultsAsync(result, cancellationToken);
                _logger.LogInformation("[AdvancedAI] Analysis completed successfully. Quantum Boost: {QuantumBoost}%, " +
                    "Risk Level: {RiskLevel}, Trading Confidence: {TradingConfidence}%",
                    result.QuantumBoostFactor, result.RiskLevel, result.TradingConfidence);
            }
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "[AdvancedAI] Failed to parse AI analysis results");
        }
    }

    private async Task CacheAIResultsAsync(AdvancedAIResult result, CancellationToken cancellationToken)
    {
        var db = _cache.GetDatabase(0);
        var timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var ttl = TimeSpan.FromMinutes(30); // Cache for 30 minutes

        // Cache individual metrics
        await db.StringSetAsync("ai:quantum:boost", result.QuantumBoostFactor.ToString("F2"), ttl);
        await db.StringSetAsync("ai:neural:confidence", result.TradingConfidence.ToString("F2"), ttl);
        await db.StringSetAsync("ai:risk:level", result.RiskLevel, ttl);
        await db.StringSetAsync("ai:predictive:alerts", result.PredictiveAlerts.ToString(), ttl);
        await db.StringSetAsync("ai:kpi:score", result.KPIScore.ToString("F2"), ttl);
        await db.StringSetAsync("ai:timestamp", timestamp, ttl);

        // Cache full report
        var json = JsonSerializer.Serialize(result);
        await db.StringSetAsync("ai:analysis:report", json, ttl);

        _logger.LogDebug("[AdvancedAI] Cached AI analysis results to Redis/Cache");
    }

    private class AdvancedAIResult
    {
        public double QuantumBoostFactor { get; set; }
        public double TradingConfidence { get; set; }
        public string RiskLevel { get; set; } = "MEDIUM";
        public int PredictiveAlerts { get; set; }
        public double KPIScore { get; set; }
        public string Timestamp { get; set; } = string.Empty;
        public Dictionary<string, object> Details { get; set; } = new();
    }
}
