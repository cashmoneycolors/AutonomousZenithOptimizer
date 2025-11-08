using System;
using System.Collections.Generic;
using System.Linq;

namespace ZenithCoreSystem.Modules
{
    public static class ZenithLogger
    {
        public static void LogAutonomousCycle(string message, Dictionary<string, object> properties)
        {
            var propsString = string.Join(", ", properties.Select(kvp => $"{kvp.Key}: {kvp.Value}"));
            var originalColor = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine($"\n[OPS OMEGA LOG] {message}");
            Console.ForegroundColor = ConsoleColor.Gray;
            Console.WriteLine($"  -> PROPERTIES: {{ {propsString} }}");
            Console.ForegroundColor = originalColor;
        }

        public static void LogCriticalError(string message, string component)
        {
            var originalColor = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[OPS OMEGA CRITICAL] {component} FEHLER: {message}");
            Console.ForegroundColor = originalColor;
        }
    }

    public class RegulatoryHyperAdaptor
    {
        private readonly Random _random = new();

        public bool PerformComplianceMock() => _random.Next(0, 10) > 1;

        public bool PerformLegalIntegrityCheck(Order order) => order.DestinationCountry != "FR" || order.Price <= 1000m;
    }

    public class AetherArchitecture
    {
        public void RouteLowLatencyEvent(string message)
        {
            Console.WriteLine($"[AetherArch] Event geroutet: {message}");
        }
    }
}
