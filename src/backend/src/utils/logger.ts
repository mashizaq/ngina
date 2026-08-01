// Minimal logger shim for the TypeScript publisher
export const logger = {
  error: (...args: any[]) => console.error(...args),
  debug: (...args: any[]) => console.debug(...args),
};
