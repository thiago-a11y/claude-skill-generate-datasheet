import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("codedocs", {
  version: "1.0.0",
});
