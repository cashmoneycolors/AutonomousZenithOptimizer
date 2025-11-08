using System;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Modules
{
    public class QML_Python_Bridge : IProfitGuarantor_QML
    {
        private readonly bool _simulateFailure;
        private int _callCount;

        public QML_Python_Bridge(bool simulateFailure = false)
        {
            _simulateFailure = simulateFailure;
            _callCount = 0;
        }

        public async Task<string> GetNAVOptimizedDecision(DRL_StateVector currentVector)
        {
            _callCount++;

            if (_simulateFailure && _callCount <= 2)
            {
                throw new TimeoutException("QML-Core ist ueberlastet oder offline (Simuliert).");
            }

            await Task.Delay(10);

            return currentVector.PredictedNAV > 140000m ? "SCALE_UP:2.0" : "MAINTAIN_LEVEL:1.0";
        }

        public Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken)
        {
            Console.WriteLine("[QML Bridge] Performance Feedback an DRL-Server gesendet.");
            return Task.Delay(50);
        }
    }
}
