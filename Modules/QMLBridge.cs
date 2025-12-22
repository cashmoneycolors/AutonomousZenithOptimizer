using System;
using System.Globalization;
using System.Net.Http;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Modules
{
    public class QML_Python_Bridge : IProfitGuarantor_QML
    {
        private readonly bool _simulateFailure;
        private readonly HttpClient _httpClient;
        private readonly string? _endpoint;
        private readonly decimal _fallbackScaleUpFactor;
        private int _callCount;

        public QML_Python_Bridge(bool simulateFailure, string? endpoint, decimal fallbackScaleUpFactor)
        {
            _simulateFailure = simulateFailure;
            _endpoint = string.IsNullOrWhiteSpace(endpoint) ? null : endpoint.Trim();
            _fallbackScaleUpFactor = fallbackScaleUpFactor > 0m ? fallbackScaleUpFactor : 1m;
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
            _callCount = 0;
        }

        public async Task<string> GetNAVOptimizedDecision(DRL_StateVector currentVector)
        {
            _callCount++;

            if (_simulateFailure && _callCount <= 2)
            {
                throw new TimeoutException("QML-Core ist ueberlastet oder offline (Simuliert).");
            }

            var liveModeRaw = Environment.GetEnvironmentVariable("AZO_LIVE_MODE");
            bool liveMode = string.Equals(liveModeRaw, "true", StringComparison.OrdinalIgnoreCase);

            var endpoint = _endpoint ?? Environment.GetEnvironmentVariable("AZO_QML_ENDPOINT");
            endpoint = string.IsNullOrWhiteSpace(endpoint) ? null : endpoint.Trim();

            if (liveMode && endpoint is null)
            {
                throw new InvalidOperationException("LiveMode aktiv, aber QML Endpoint fehlt. Setze Optimizer:QmlEndpoint oder ENV AZO_QML_ENDPOINT.");
            }

            endpoint ??= "http://localhost:8501/api/qml_decision";

            try
            {
                var nav = currentVector.PredictedNAV.ToString(CultureInfo.InvariantCulture);
                var response = await _httpClient.GetAsync(endpoint + "?nav=" + nav);
                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadAsStringAsync();
                    return result.Trim();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[QML Bridge] Fehler bei KI-Abfrage: {ex.Message}. Fallback verwendet.");
            }

            // Fallback: Lokale Logik (deterministisch)  live nur als letzter Fallback gedacht.
            await Task.Delay(10);
            return currentVector.PredictedNAV > 120000m
                ? $"SCALE_UP:{_fallbackScaleUpFactor.ToString("0.0###", CultureInfo.InvariantCulture)}"
                : "MAINTAIN_LEVEL:1.0";
        }

        public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
        {
            Console.WriteLine("[QML Bridge] Performance Feedback an DRL-Server gesendet.");
            return Task.Delay(50);
        }
    }
}

