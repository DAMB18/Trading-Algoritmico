using System;
using System.Linq;
using System.Globalization;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;
using System.Collections.Generic;
using System.Net;
using System.IO;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class DeepTradingSniperV6 : Robot
    {
        // --- PARÁMETROS DE FILTRADO ---
        [Parameter("Buy Threshold", DefaultValue = 0.72)]
        public double BuyThreshold { get; set; }

        [Parameter("Sell Threshold", DefaultValue = 0.28)]
        public double SellThreshold { get; set; }

        [Parameter("Meta Diaria ($)", DefaultValue = 500)]
        public double DailyProfitTarget { get; set; }

        [Parameter("Monto a Arriesgar ($)", DefaultValue = 200)]
        public double RiskAmount { get; set; }
        
        // --- PARÁMETROS TRAILING STOP (DeMark/Zúrich) ---
        [Parameter("Activar Trailing a ($)", DefaultValue = 50)]
        public double TriggerTrailingAmount { get; set; }

        private AverageTrueRange _atr;
        private double _dailyStartingEquity;
        private const string BotLabel = "Sniper_V6_Attention";

        protected override void OnStart()
        {
            _atr = Indicators.AverageTrueRange(24, MovingAverageType.Exponential);
            _dailyStartingEquity = Account.Equity;
            Print("Sniper V6 Iniciado. Modelo de Atención Cargado.");
        }

        protected override void OnBar()
        {
            // 1. Control de Meta Diaria
            if (Account.Equity - _dailyStartingEquity >= DailyProfitTarget)
            {
                Print("Meta diaria alcanzada. Bot en pausa.");
                return;
            }

            // 2. Filtro Horario Nueva York (9:30 - 16:00 EST)
            var nyTimeZone = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
            var nyTime = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, nyTimeZone);
            bool isNySession = (nyTime.Hour >= 9 && nyTime.Minute >= 30) && (nyTime.Hour < 16);

            if (!isNySession) return;

            try 
            {
                // Aquí iría tu función GetSocketPrediction(rawData) que ya tienes implementada
                double prediction = 0.5; // Placeholder para la llamada al servidor Python
                
                // 3. Ejecución de Señales
                if (prediction >= BuyThreshold)
                    ExecuteSniperTrade(TradeType.Buy, prediction);
                else if (prediction <= SellThreshold)
                    ExecuteSniperTrade(TradeType.Sell, prediction);
            }
            catch (Exception ex)
            {
                Print("Error en predicción: {0}", ex.Message);
            }
        }

        protected override void OnTick()
        {
            // --- GESTIÓN DE TRAILING STOP (Axiomas de Zúrich) ---
            foreach (var position in Positions.Where(p => p.Label == BotLabel))
            {
                double currentProfit = position.GrossProfit;

                // Si la posición gana más de TriggerTrailingAmount ($50), protegemos a Breakeven
                if (currentProfit >= TriggerTrailingAmount)
                {
                    if (position.TradeType == TradeType.Buy && position.StopLoss < position.EntryPrice)
                    {
                        ModifyPosition(position, position.EntryPrice, position.TakeProfit);
                        Print("Trailing: Posición Buy protegida en Breakeven.");
                    }
                    else if (position.TradeType == TradeType.Sell && position.StopLoss > position.EntryPrice)
                    {
                        ModifyPosition(position, position.EntryPrice, position.TakeProfit);
                        Print("Trailing: Posición Sell protegida en Breakeven.");
                    }
                }
            }
        }

        private void ExecuteSniperTrade(TradeType type, double pred)
        {
            double atrVal = _atr.Result.Last(1);
            if (atrVal == 0) return;

            // Distancias basadas en volatilidad (DeMark)
            double slPips = (atrVal * 1.5) / Symbol.PipSize;
            double tpPips = (atrVal * 1.0) / Symbol.PipSize;

            // Cálculo de Volumen para arriesgar RiskAmount ($200)
            double volume = Symbol.NormalizeVolumeInUnits(RiskAmount / (slPips * Symbol.PipValue * 10));

            var result = ExecuteMarketOrder(type, SymbolName, volume, BotLabel, slPips, tpPips);
            
            if (result.IsSuccessful)
                Print("Sniper Entry: {0} (Confianza: {1:F4})", type, pred);
        }
    }
}