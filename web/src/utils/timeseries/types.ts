export interface TimeSeriesPoint {
  x: number;
  y: number;
}

export interface TimeSeriesData {
  series: { name: string; data: TimeSeriesPoint[] }[];
}
