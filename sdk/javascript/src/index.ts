/**
 * Clawdex TypeScript SDK
 *
 * The official SDK for interacting with Clawdex - the collective AI coding agent brain.
 * Every verified fix makes ALL AI agents smarter.
 *
 * @packageDocumentation
 *
 * @example
 * Basic Usage
 * ```typescript
 * import { ClawdexClient } from 'clawdex';
 *
 * const clawdex = new ClawdexClient();
 *
 * // Find solutions for an error
 * const result = await clawdex.findSolution({
 *   errorMessage: 'Cannot find module react',
 *   language: 'typescript'
 * });
 *
 * // Log an error fix
 * await clawdex.logErrorFix({
 *   errorMessage: 'Module not found',
 *   solution: 'Run npm install'
 * });
 * ```
 *
 * @example
 * With Custom Configuration
 * ```typescript
 * import { ClawdexClient } from 'clawdex';
 *
 * const clawdex = new ClawdexClient({
 *   apiUrl: 'http://localhost:8000',
 *   timeout: 60000,
 *   debug: true
 * });
 * ```
 *
 * @example
 * Error Handling
 * ```typescript
 * import { ClawdexClient, NetworkError, ValidationError } from 'clawdex';
 *
 * const clawdex = new ClawdexClient();
 *
 * try {
 *   await clawdex.findSolution({ errorMessage: '' });
 * } catch (error) {
 *   if (error instanceof ValidationError) {
 *     console.log('Invalid input:', error.field);
 *   } else if (error instanceof NetworkError) {
 *     console.log('Network issue:', error.message);
 *   }
 * }
 * ```
 */

// Main client
export { ClawdexClient } from "./client.js";

// Error classes
export {
  ClawdexError,
  NetworkError,
  ApiError,
  TimeoutError,
  ValidationError,
  AuthenticationError,
  RateLimitError,
  NotFoundError,
} from "./errors.js";

// Types
export type {
  // Configuration
  ClawdexClientOptions,

  // Context
  Context,

  // Error Fix types
  ErrorInfo,
  SolutionInfo,
  LogErrorFixOptions,
  FindSolutionOptions,
  Solution,
  FindSolutionResult,

  // Decision types
  LogDecisionOptions,
  FindDecisionOptions,
  Decision,
  FindDecisionResult,

  // Pattern types
  LogPatternOptions,
  FindPatternOptions,
  Pattern,
  FindPatternResult,

  // Verification types
  VerifySolutionOptions,
  VerifySolutionResult,

  // Stats types
  ClawdexStats,
  StatsResult,

  // Generic result types
  LogResult,
} from "./types.js";

// Version
export const VERSION = "0.1.0";

// Default export for convenience
export { ClawdexClient as default } from "./client.js";
