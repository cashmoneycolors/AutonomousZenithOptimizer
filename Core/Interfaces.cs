using System;
using System.Threading.Tasks;

namespace ZenithCoreSystem
{
    public interface IAutonomousZenithOptimizer
    {
        Task RunAutonomousGrowthStrategy();
        Task ProcessIncomingOrder(Order order);
    }

    public interface IProfitGuarantor_QML
    {
        Task<string> GetNAVOptimizedDecision(DRL_StateVector currentVector);
        Task ReportPerformanceFeedback(string vector, decimal roasScore, string actionTaken);
    }

    public interface IHyperCache
    {
        Task<string?> GetAsync(string key);
        Task SetAsync(string key, string value, TimeSpan expiry);
    }

    public interface IHFT_AMAD_Adapter
    {
        Task<decimal> ExecuteTrade(string symbol, decimal amount, string direction);
    }

    public interface IGEF_MSA_Adapter
    {
        Task<string> GenerateText(string prompt, string styleGuide);
    }

    public interface IECA_AHA_Adapter
    {
        Task<bool> SubmitOrder(Order order, string supplierID);
    }
}
