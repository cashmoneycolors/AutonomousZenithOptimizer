using System;
using System.Globalization;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Modules
{
    public class QML_Python_Bridge : IProfitGuarantor_QML
    {
        private readonly bool _simulateFailure;
        private readonly HttpClient _httpClient;
        private readonly string? _endpoint;
        private readonly ILogger<QML_Python_Bridge>? _logger;
        private int _callCount;
        private DateTimeOffset _nextErrorLogAtUtc = DateTimeOffset.MinValue;

        public QML_Python_Bridge(bool simulateFailure, string? endpoint, ILogger<QML_Python_Bridge>? logger = null)
        {
            _simulateFailure = simulateFailure;
            _endpoint = string.IsNullOrWhiteSpace(endpoint) ? null : endpoint.Trim();
            _logger = logger;
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

            var nav = currentVector.PredictedNAV.ToString(CultureInfo.InvariantCulture);
            var requestUri = endpoint + "?nav=" + nav;

            try
            {
                using var response = await _httpClient.GetAsync(requestUri);
                response.EnsureSuccessStatusCode();
                var result = await response.Content.ReadAsStringAsync();
                return result.Trim();
            }
            catch (Exception ex)
            {
                // Wichtig: Nicht stillschweigend "SCALE_UP" o.ä. zurückgeben.
                // Wenn der Decision-Service nicht erreichbar ist, muss das Orchestrator-Retry greifen
                // und am Ende deterministisch auf MAINTAIN zurückfallen.
                var now = DateTimeOffset.UtcNow;
                if (now >= _nextErrorLogAtUtc)
                {
                    _logger?.LogWarning(ex, "QML Endpoint nicht erreichbar: {Endpoint}. Request: {RequestUri}", endpoint, requestUri);
                    _nextErrorLogAtUtc = now.AddSeconds(30);
                }

                throw;
            }
        }

        public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
        {
            Console.WriteLine("[QML Bridge] Performance Feedback an DRL-Server gesendet.");
            return Task.Delay(50);
        }
    }
}

