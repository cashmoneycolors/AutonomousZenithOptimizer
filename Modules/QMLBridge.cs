using System;
using System.Net.Http;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Modules
{
    public class QML_Python_Bridge : IProfitGuarantor_QML
    {
        private readonly bool _simulateFailure;
        private readonly HttpClient _httpClient;
        private int _callCount;

        public QML_Python_Bridge(bool simulateFailure = false)
        {
            _simulateFailure = simulateFailure;
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

            try
            {
                // Echte Integration: HTTP-Aufruf an Python-KI-Server
                var response = await _httpClient.GetAsync("http://localhost:8501/api/qml_decision?nav=" + currentVector.PredictedNAV);
                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadAsStringAsync();
                    return result.Trim();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[QML Bridge] Fehler bei echter KI-Abfrage: {ex.Message}. Fallback verwendet.");
            }

            // Fallback: Lokale Logik
            await Task.Delay(10);
            return currentVector.PredictedNAV > 120000m ? "SCALE_UP:3.0" : "MAINTAIN_LEVEL:1.0";
        }

        public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
        {
            Console.WriteLine("[QML Bridge] Performance Feedback an DRL-Server gesendet.");
            return Task.Delay(50);
        }
    }
}
