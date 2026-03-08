export interface TableData {
  headers: string[];
  rows: string[][];
}

export interface TableSection {
  heading?: string;
  table: TableData;
}
