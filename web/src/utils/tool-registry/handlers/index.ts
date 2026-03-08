import type { ToolHandler } from "../types.js";
import { mtvReadHandlers } from "./mtv-read.js";
import { mtvWriteHandlers } from "./mtv-write.js";
import { mtvHelpHandlers } from "./mtv-help.js";
import { metricsReadHandlers } from "./metrics-read.js";
import { metricsHelpHandlers } from "./metrics-help.js";
import { debugReadHandlers } from "./debug-read.js";
import { debugHelpHandlers } from "./debug-help.js";

export const allHandlers: ToolHandler[] = [
  ...mtvReadHandlers,
  ...mtvWriteHandlers,
  ...mtvHelpHandlers,
  ...metricsReadHandlers,
  ...metricsHelpHandlers,
  ...debugReadHandlers,
  ...debugHelpHandlers,
];
