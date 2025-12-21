using System;
using System.Globalization;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;

namespace ZenithCoreSystem.Modules
{
    public static class ZenithLogger
    {
        public static void LogAutonomousCycle(this ILogger logger, string message, IReadOnlyDictionary<string, object> properties)
        {
            if (!logger.IsEnabled(LogLevel.Information))
            {
                return;
            }

            var scopeValues = new Dictionary<string, object>();
            foreach (var kvp in properties)
            {
                scopeValues[kvp.Key] = kvp.Value;
            }

            using var scope = logger.BeginScope(scopeValues);
            logger.LogInformation("OPS OMEGA LOG | {Message}", message);
        }

        public static void LogCriticalError(this ILogger logger, string message, string component)
        {
            if (!logger.IsEnabled(LogLevel.Critical))
            {
                return;
            }

            using var scope = logger.BeginScope(new Dictionary<string, object>
            {
                { "Component", component }
            });

            logger.LogCritical("OPS OMEGA CRITICAL | {Message}", message);
        }
    }

        public class RegulatoryHyperAdaptor
    {
        public double GetComplianceScore()
        {
            var scoreRaw = Environment.GetEnvironmentVariable("AZO_COMPLIANCE_SCORE");
            if (!string.IsNullOrWhiteSpace(scoreRaw))
            {
                var normalized = scoreRaw.Replace(',', '.');
                if (double.TryParse(normalized, NumberStyles.Float, CultureInfo.InvariantCulture, out var score))
                {
                    return Math.Clamp(score, 0.0, 1.0);
                }
            }

            var approvedRaw = Environment.GetEnvironmentVariable("AZO_COMPLIANCE_APPROVED");
            if (string.Equals(approvedRaw, "true", StringComparison.OrdinalIgnoreCase))
            {
                return 0.99;
            }

            if (string.Equals(approvedRaw, "false", StringComparison.OrdinalIgnoreCase))
            {
                return 0.0;
            }

            // Konservativer Default: nicht "Random", aber auch nicht immer "Top-Score".
            return 0.75;
        }

        public bool PerformLegalIntegrityCheck(Order order) =>
            order.DestinationCountry != "FR" || order.Price <= 10000m;
    }

    public class AetherArchitecture
    {
        public void RouteLowLatencyEvent(string message)
        {
            Console.WriteLine($"[AetherArch] Event geroutet: {message}");
        }
    }
}

