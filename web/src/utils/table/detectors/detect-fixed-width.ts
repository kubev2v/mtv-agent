/** True when text looks like a fixed-width (space-aligned) table. */
export function hasFixedWidthTable(text: string): boolean {
  const lines = text.split("\n").filter((l) => l.trim());
  if (lines.length < 2) return false;
  const header = lines[0];
  let spaces = 0;
  let cols = 1;
  for (let i = 0; i < header.length; i++) {
    if (header[i] === " ") {
      spaces++;
    } else {
      if (spaces >= 2) cols++;
      spaces = 0;
    }
  }
  return cols >= 2;
}
