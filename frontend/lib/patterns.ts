export type PatternTime = string | number;
export type PatternCandle = {
  time: PatternTime;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};
export type PatternPoint = { time: PatternTime; value: number };
export type PatternMarker = {
  time: PatternTime;
  position: "aboveBar" | "belowBar";
  shape: "arrowUp" | "arrowDown" | "circle";
  text: string;
};
export type PatternOverlay = {
  id: string;
  label: string;
  color: string;
  lines: PatternPoint[][];
  marker?: PatternMarker;
};

const COLORS = ["#50f2a7", "#60a5fa", "#fbbf24", "#f472b6", "#a78bfa", "#fb7185"];
const LABELS: Record<string, string> = {
  tl_resistance: "Resistance trendline", tl_support: "Support trendline",
  horizontal_sr: "Horizontal S/R", channel: "Channel", channel_up: "Rising channel",
  channel_down: "Falling channel", triangle_ascending: "Ascending triangle",
  triangle_descending: "Descending triangle", wedge: "Symmetrical wedge",
  wedge_up: "Rising wedge", wedge_down: "Falling wedge", double_top: "Double top",
  double_bottom: "Double bottom", multiple_top: "Multiple top",
  multiple_bottom: "Multiple bottom", head_shoulders: "Head & shoulders",
  head_shoulders_inverse: "Inverse head & shoulders", long_lower_shadow: "Long lower shadow",
  long_upper_shadow: "Long upper shadow", hammer: "Hammer", inverted_hammer: "Inverted hammer",
  spinning_top_white: "Bullish spinning top", spinning_top_black: "Bearish spinning top",
  doji: "Doji", dragonfly_doji: "Dragonfly doji", gravestone_doji: "Gravestone doji",
  marubozu_white: "Bullish marubozu", marubozu_black: "Bearish marubozu",
};

function average(values: number[]) { return values.reduce((sum, value) => sum + value, 0) / values.length; }
function fit(values: number[], xs = values.map((_, index) => index)) {
  const xm = average(xs); const ym = average(values);
  const denominator = xs.reduce((sum, x) => sum + (x - xm) ** 2, 0);
  const slope = denominator ? xs.reduce((sum, x, index) => sum + (x - xm) * (values[index] - ym), 0) / denominator : 0;
  const intercept = ym - slope * xm;
  const rmse = Math.sqrt(average(values.map((value, index) => (value - (intercept + slope * xs[index])) ** 2)));
  return { slope, intercept, rmse };
}
function atr(bars: PatternCandle[]) {
  const start = Math.max(1, bars.length - 14); const ranges = [];
  for (let index = start; index < bars.length; index++) {
    const bar = bars[index]; const previous = bars[index - 1].close;
    ranges.push(Math.max(bar.high - bar.low, Math.abs(bar.high - previous), Math.abs(bar.low - previous)));
  }
  return ranges.length ? average(ranges) : Math.max(bars.at(-1)!.high - bars.at(-1)!.low, 0.01);
}
function swings(window: PatternCandle[], highs: boolean) {
  const points: { index: number; value: number }[] = [];
  const values = window.map((bar) => highs ? bar.high : bar.low);
  for (let index = 2; index < values.length - 2; index++) {
    const neighbors = [...values.slice(index - 2, index), ...values.slice(index + 1, index + 3)];
    if ((highs && values[index] >= Math.max(...neighbors)) || (!highs && values[index] <= Math.min(...neighbors))) points.push({ index, value: values[index] });
  }
  return points;
}
function candlePatterns(bar: PatternCandle, averageRange: number) {
  const range = Math.max(bar.high - bar.low, 1e-12); const body = Math.abs(bar.close - bar.open);
  const upper = bar.high - Math.max(bar.open, bar.close); const lower = Math.min(bar.open, bar.close) - bar.low;
  const bodyRatio = body / range; const upperRatio = upper / range; const lowerRatio = lower / range;
  const closeLocation = (bar.close - bar.low) / range; const referenceBody = Math.max(body, range * .05);
  const found: string[] = [];
  if (lowerRatio >= .6 && closeLocation >= .5) found.push("long_lower_shadow");
  if (upperRatio >= .6 && closeLocation <= .5) found.push("long_upper_shadow");
  if (lower >= 2 * referenceBody && upperRatio <= .25 && closeLocation >= .65) found.push("hammer");
  if (upper >= 2 * referenceBody && lowerRatio <= .25 && closeLocation <= .35) found.push("inverted_hammer");
  if (bodyRatio <= .35 && upperRatio >= .15 && lowerRatio >= .15) found.push(bar.close >= bar.open ? "spinning_top_white" : "spinning_top_black");
  if (bodyRatio <= .1) {
    found.push("doji");
    if (lowerRatio >= .6 && upperRatio <= .1 && closeLocation >= .85) found.push("dragonfly_doji");
    if (upperRatio >= .6 && lowerRatio <= .1 && closeLocation <= .15) found.push("gravestone_doji");
  }
  if (range >= .75 * averageRange && bodyRatio >= .9) found.push(bar.close > bar.open ? "marubozu_white" : "marubozu_black");
  return found;
}

export function detectPatternOverlays(bars: PatternCandle[]): PatternOverlay[] {
  if (bars.length < 30) return [];
  const window = bars.slice(-30); const lineWindow = window.slice(-20); const last = bars.at(-1)!;
  const currentAtr = atr(bars); const price = Math.max(last.close, 1e-12);
  const xs = [2, 7, 12, 17];
  const upper = [0, 5, 10, 15].map((start) => Math.max(...lineWindow.slice(start, start + 5).map((bar) => bar.high)));
  const lower = [0, 5, 10, 15].map((start) => Math.min(...lineWindow.slice(start, start + 5).map((bar) => bar.low)));
  const highFit = fit(upper, xs); const lowFit = fit(lower, xs);
  const highStart = highFit.intercept; const lowStart = lowFit.intercept;
  const highNow = highFit.intercept + highFit.slope * 19; const lowNow = lowFit.intercept + lowFit.slope * 19;
  const widthStart = Math.max(highStart - lowStart, 1e-12); const widthNow = Math.max(highNow - lowNow, 1e-12);
  const highSlope = highFit.slope / price; const lowSlope = lowFit.slope / price;
  const horizontal = .0008; const directional = .0004;
  const highGood = highFit.rmse <= Math.max(currentAtr, price * .02); const lowGood = lowFit.rmse <= Math.max(currentAtr, price * .02);
  const converging = widthNow <= .85 * widthStart; const stable = Math.abs(widthNow / widthStart - 1) <= .25;
  const parallel = Math.abs(highSlope - lowSlope) <= .0008;
  const highHorizontal = Math.abs(highSlope) <= horizontal; const lowHorizontal = Math.abs(lowSlope) <= horizontal;
  const highPositive = highSlope >= directional; const lowPositive = lowSlope >= directional;
  const highNegative = highSlope <= -directional; const lowNegative = lowSlope <= -directional;
  const nearResistance = Math.abs(highNow - last.close) <= currentAtr; const nearSupport = Math.abs(last.close - lowNow) <= currentAtr;
  const startTime = lineWindow[0].time; const endTime = lineWindow.at(-1)!.time;
  const boundaries = [
    [{ time: startTime, value: highStart }, { time: endTime, value: highNow }],
    [{ time: startTime, value: lowStart }, { time: endTime, value: lowNow }],
  ];
  const detected: { id: string; lines: PatternPoint[][] }[] = [];
  if (highGood && nearResistance) detected.push({ id: "tl_resistance", lines: [boundaries[0]] });
  if (lowGood && nearSupport) detected.push({ id: "tl_support", lines: [boundaries[1]] });
  if (highHorizontal && highGood && nearResistance) detected.push({ id: "horizontal_sr", lines: [boundaries[0]] });
  if (highHorizontal && lowHorizontal && highGood && lowGood && stable) detected.push({ id: "channel", lines: boundaries });
  if (highHorizontal && lowPositive && converging && highGood && lowGood) detected.push({ id: "triangle_ascending", lines: boundaries });
  if (lowHorizontal && highNegative && converging && highGood && lowGood) detected.push({ id: "triangle_descending", lines: boundaries });
  if (highNegative && lowPositive && converging && highGood && lowGood) detected.push({ id: "wedge", lines: boundaries });
  if (highPositive && lowPositive && lowFit.slope > highFit.slope && converging) detected.push({ id: "wedge_up", lines: boundaries });
  if (highNegative && lowNegative && highFit.slope < lowFit.slope && converging) detected.push({ id: "wedge_down", lines: boundaries });
  if (highPositive && lowPositive && parallel && stable) detected.push({ id: "channel_up", lines: boundaries });
  if (highNegative && lowNegative && parallel && stable) detected.push({ id: "channel_down", lines: boundaries });

  const peaks = swings(window, true); const troughs = swings(window, false);
  const tolerance = Math.max(.01 * price, .75 * currentAtr); const priorChange = last.close / window[0].close - 1;
  const pivotLine = (points: { index: number; value: number }[]) => points.map((point) => ({ time: window[point.index].time, value: point.value }));
  if (peaks.length >= 2) {
    const points = peaks.slice(-2); if (points[1].index - points[0].index >= 4 && Math.abs(points[1].value - points[0].value) <= tolerance && priorChange > 0) detected.push({ id: "double_top", lines: [pivotLine(points)] });
  }
  if (troughs.length >= 2) {
    const points = troughs.slice(-2); if (points[1].index - points[0].index >= 4 && Math.abs(points[1].value - points[0].value) <= tolerance && priorChange < 0) detected.push({ id: "double_bottom", lines: [pivotLine(points)] });
  }
  if (peaks.length >= 3) {
    const points = peaks.slice(-3); const values = points.map((point) => point.value);
    if (Math.max(...values) - Math.min(...values) <= tolerance && priorChange > 0) detected.push({ id: "multiple_top", lines: [pivotLine(points)] });
    if (Math.abs(values[0] - values[2]) <= tolerance && values[1] >= Math.max(values[0], values[2]) + .5 * currentAtr) detected.push({ id: "head_shoulders", lines: [pivotLine(points)] });
  }
  if (troughs.length >= 3) {
    const points = troughs.slice(-3); const values = points.map((point) => point.value);
    if (Math.max(...values) - Math.min(...values) <= tolerance && priorChange < 0) detected.push({ id: "multiple_bottom", lines: [pivotLine(points)] });
    if (Math.abs(values[0] - values[2]) <= tolerance && values[1] <= Math.min(values[0], values[2]) - .5 * currentAtr) detected.push({ id: "head_shoulders_inverse", lines: [pivotLine(points)] });
  }

  const overlays: PatternOverlay[] = detected.map((pattern, index) => ({ ...pattern, label: LABELS[pattern.id], color: COLORS[index % COLORS.length] }));
  for (const id of candlePatterns(last, currentAtr)) {
    overlays.push({ id, label: LABELS[id], color: COLORS[overlays.length % COLORS.length], lines: [], marker: { time: last.time, position: id.includes("lower") || id.includes("hammer") || id.includes("dragonfly") || id.includes("white") ? "belowBar" : "aboveBar", shape: id.includes("lower") || id.includes("hammer") || id.includes("dragonfly") || id.includes("white") ? "arrowUp" : "arrowDown", text: LABELS[id] } });
  }
  return overlays;
}
