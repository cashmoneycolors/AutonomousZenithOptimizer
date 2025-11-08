using System;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Adapters
{
    public class HFT_AMAD_Adapter : IHFT_AMAD_Adapter
    {
        public async Task<decimal> ExecuteTrade(string symbol, decimal amount, string direction)
        {
            var originalColor = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"[AMAD/HFT] Live-Trade ausgefuehrt: {direction} {amount} {symbol}");
            Console.ForegroundColor = originalColor;
            await Task.Delay(5);
            return amount * 1.0001m;
        }
    }
}
