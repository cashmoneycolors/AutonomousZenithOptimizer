using System;
using System.Threading.Tasks;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Adapters
{
    public class ECA_AHA_Adapter : IECA_AHA_Adapter
    {
        public async Task<bool> SubmitOrder(Order order, string supplierID)
        {
            if (string.Equals(Environment.GetEnvironmentVariable("AZO_LIVE_MODE"), "true", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("LiveMode aktiv, aber ECA_AHA_Adapter ist ein Stub. Bitte echte CRM/Order-API integrieren (kein Console+Delay).");
            }

            Console.WriteLine($"[AHA/ECA] Order {order.OrderID} an Supplier {supplierID} via CRM/API gesendet.");
            await Task.Delay(50);
            return true;
        }
    }
}
