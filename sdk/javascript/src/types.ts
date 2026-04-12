/**
 * Clawdex TypeScript SDK - Type Definitions
 *
 * Complete type definitions for the Clawdex collective AI coding agent brain.
 * All types are exported for use in consuming applications.
 *
 * @module clawdex/types
 */

// =============================================================================
// Configuration Types
// =============================================================================

/**
 * Configuration options for the ClawdexClient
 */
export interface ClawdexClientOptions {
  /**
   * Base URL of the Clawdex API server
   * @default "https://api.clawdex.dev"
   * @example "http://localhost:8000"
   */
  apiUrl?: string;

  /**
   * API key for authenticated requests (optional, for future use)
   */
  apiKey?: string;

  /**
   * Request timeout in milliseconds
   * @default 30000
   */
  timeout?: number;

  /**
   * Custom headers to include in all requests
   */
  headers?: Record<string, string>;

  /**
   * Enable debug logging
   * @default false
   */
  debug?: boolean;
}

// =============================================================================
// Context Types
// =============================================================================

/**
 * Context information for matching solutions and filtering queries.
 * Providing context improves the relevance of search results.
 */
export interface Context {
  /**
   * Project name or identifier
   * @example "my-webapp"
   */
  project?: string;

  /**
   * Programming language
   * @example "typescript", "python", "go", "rust"
   */
  language?: string;

  /**
   * Framework being used
   * @example "nextjs", "fastapi", "express", "django"
   */
  framework?: string;

  /**
   * Database being used
   * @example "postgresql", "mongodb", "mysql", "supabase"
   */
  database?: string;

  /**
   * Deployment platform
   * @example "railway", "vercel", "aws", "gcp", "local"
   */
  platform?: string;

  /**
   * Issue category
   * @example "database", "auth", "api", "deployment", "testing"
   */
  category?: string;

  /**
   * Version information for dependencies
   * @example { "node": "20.x", "typescript": "5.x" }
   */
  versions?: Record<string, string>;
}

// =============================================================================
// Error Fix Types
// =============================================================================

/**
 * Information about an error encountered
 */
export interface ErrorInfo {
  /**
   * The error message that was encountered
   */
  message: string;

  /**
   * Type of error (e.g., "ConnectionError", "TypeError", "SyntaxError")
   */
  errorType?: string;

  /**
   * Full stack trace if available
   */
  stackTrace?: string;

  /**
   * File where the error occurred
   */
  file?: string;

  /**
   * Line number where the error occurred
   */
  line?: number;
}

/**
 * Information about a solution that was applied
 */
export interface SolutionInfo {
  /**
   * Description of how the error was fixed
   */
  description: string;

  /**
   * The actual code change made to fix the error
   */
  codeChange?: string;

  /**
   * List of files that were modified
   */
  filesModified?: string[];

  /**
   * How the solution was verified to work
   */
  verification?: string;
}

/**
 * Options for logging an error fix
 */
export interface LogErrorFixOptions {
  /**
   * The error message that was encountered (required)
   */
  errorMessage: string;

  /**
   * Description of how the error was fixed (required)
   */
  solution: string;

  /**
   * Type of error (e.g., "ConnectionError", "TypeError")
   */
  errorType?: string;

  /**
   * Full stack trace if available
   */
  stackTrace?: string;

  /**
   * File where the error occurred
   */
  file?: string;

  /**
   * Line number where the error occurred
   */
  line?: number;

  /**
   * The actual code change made to fix the error
   */
  codeChange?: string;

  /**
   * List of files that were modified
   */
  filesModified?: string[];

  /**
   * Project name
   */
  project?: string;

  /**
   * Programming language
   */
  language?: string;

  /**
   * Framework being used
   */
  framework?: string;

  /**
   * Database being used
   */
  database?: string;

  /**
   * Deployment platform
   */
  platform?: string;

  /**
   * Issue category
   */
  category?: string;

  /**
   * How long it took to fix (e.g., "5m", "2h")
   */
  timeToSolve?: string;

  /**
   * Whether the solution has been verified to work
   */
  verified?: boolean;
}

/**
 * Options for finding solutions to an error
 */
export interface FindSolutionOptions {
  /**
   * The error message to find solutions for (required)
   */
  errorMessage: string;

  /**
   * Project name for context matching
   */
  project?: string;

  /**
   * Programming language for context matching
   */
  language?: string;

  /**
   * Framework for context matching
   */
  framework?: string;

  /**
   * Database for context matching
   */
  database?: string;

  /**
   * Platform for context matching
   */
  platform?: string;

  /**
   * Issue category for context matching
   */
  category?: string;

  /**
   * Maximum number of solutions to return
   * @default 5
   */
  limit?: number;
}

/**
 * A solution found in the Clawdex knowledge base
 */
export interface Solution {
  /**
   * Unique identifier for this solution record
   */
  id: string;

  /**
   * Description of how to fix the error
   */
  solution: string;

  /**
   * The original error message this solution addresses
   */
  originalError: string;

  /**
   * Context in which this solution was applied
   */
  context: Context;

  /**
   * Confidence score (0.0 to 1.0) based on context match
   */
  confidence: number;

  /**
   * Whether this solution has been verified to work
   */
  verified: boolean;

  /**
   * Source of the solution
   */
  source: "local" | "community";
}

/**
 * Result of searching for solutions
 */
export interface FindSolutionResult {
  /**
   * Whether any solutions were found
   */
  found: boolean;

  /**
   * Human-readable message about the search results
   */
  message: string;

  /**
   * List of matching solutions, ordered by relevance
   */
  solutions: Solution[];

  /**
   * Suggestion for what to do if no solutions found
   */
  suggestion?: string;
}

// =============================================================================
// Decision Types
// =============================================================================

/**
 * Options for logging an architectural decision
 */
export interface LogDecisionOptions {
  /**
   * Short title for the decision (required)
   */
  title: string;

  /**
   * What was chosen (required)
   */
  choice: string;

  /**
   * Other options that were considered
   */
  alternatives?: string[];

  /**
   * Advantages of the chosen option
   */
  pros?: string[];

  /**
   * Disadvantages of the chosen option
   */
  cons?: string[];

  /**
   * The main reason for this choice
   */
  decidingFactor?: string;

  /**
   * Project name
   */
  project?: string;

  /**
   * Component this decision affects
   */
  component?: string;

  /**
   * Programming language context
   */
  language?: string;

  /**
   * Framework context
   */
  framework?: string;
}

/**
 * Options for finding past decisions
 */
export interface FindDecisionOptions {
  /**
   * Topic to search for (required)
   * @example "database choice", "auth strategy", "state management"
   */
  topic: string;

  /**
   * Filter by project
   */
  project?: string;

  /**
   * Filter by component
   */
  component?: string;

  /**
   * Maximum number of decisions to return
   * @default 3
   */
  limit?: number;
}

/**
 * A decision found in the Clawdex knowledge base
 */
export interface Decision {
  /**
   * Unique identifier for this decision record
   */
  id: string;

  /**
   * Short title for the decision
   */
  title: string;

  /**
   * What was chosen
   */
  choice: string;

  /**
   * Other options that were considered
   */
  alternatives: string[];

  /**
   * Relevance score (0.0 to 1.0)
   */
  relevance: number;
}

/**
 * Result of searching for decisions
 */
export interface FindDecisionResult {
  /**
   * Whether any decisions were found
   */
  found: boolean;

  /**
   * Human-readable message about the search results
   */
  message: string;

  /**
   * List of matching decisions, ordered by relevance
   */
  decisions: Decision[];

  /**
   * Suggestion for what to do if no decisions found
   */
  suggestion?: string;
}

// =============================================================================
// Pattern Types
// =============================================================================

/**
 * Options for logging a reusable pattern
 */
export interface LogPatternOptions {
  /**
   * Name for this pattern (required)
   */
  name: string;

  /**
   * Category of the pattern (required)
   * @example "database", "auth", "api", "deployment", "testing", "frontend"
   */
  category: string;

  /**
   * The problem this pattern solves (required)
   */
  problem: string;

  /**
   * How the pattern solves the problem (required)
   */
  solution: string;

  /**
   * Languages this pattern applies to
   */
  languages?: string[];

  /**
   * Frameworks this pattern applies to
   */
  frameworks?: string[];

  /**
   * Databases this pattern applies to
   */
  databases?: string[];

  /**
   * Scenarios where this pattern is useful
   */
  scenarios?: string[];

  /**
   * Code before applying the pattern
   */
  beforeCode?: string;

  /**
   * Code after applying the pattern
   */
  afterCode?: string;

  /**
   * Detailed explanation of the pattern
   */
  explanation?: string;
}

/**
 * Options for finding patterns
 */
export interface FindPatternOptions {
  /**
   * The problem to find patterns for (required)
   */
  problem: string;

  /**
   * Category filter
   */
  category?: string;

  /**
   * Language filter
   */
  language?: string;

  /**
   * Framework filter
   */
  framework?: string;

  /**
   * Maximum number of patterns to return
   * @default 3
   */
  limit?: number;
}

/**
 * A pattern found in the Clawdex knowledge base
 */
export interface Pattern {
  /**
   * Unique identifier for this pattern record
   */
  id: string;

  /**
   * Name of the pattern
   */
  name: string;

  /**
   * Category of the pattern
   */
  category: string;

  /**
   * The problem this pattern solves
   */
  problem: string;

  /**
   * How the pattern solves the problem
   */
  solution: string;

  /**
   * Relevance score (0.0 to 1.0)
   */
  relevance: number;
}

/**
 * Result of searching for patterns
 */
export interface FindPatternResult {
  /**
   * Whether any patterns were found
   */
  found: boolean;

  /**
   * Human-readable message about the search results
   */
  message: string;

  /**
   * List of matching patterns, ordered by relevance
   */
  patterns: Pattern[];

  /**
   * Suggestion for what to do if no patterns found
   */
  suggestion?: string;
}

// =============================================================================
// Verification Types
// =============================================================================

/**
 * Options for verifying a solution
 */
export interface VerifySolutionOptions {
  /**
   * The record ID of the solution to verify (required)
   */
  id: string;

  /**
   * Whether the solution worked (required)
   */
  success: boolean;
}

/**
 * Result of verifying a solution
 */
export interface VerifySolutionResult {
  /**
   * Whether the verification was successful
   */
  success: boolean;

  /**
   * Human-readable message about the verification
   */
  message: string;

  /**
   * The record ID that was verified
   */
  recordId: string;

  /**
   * How the solution was verified
   */
  verifiedAs: "successful" | "unsuccessful";

  /**
   * Whether the solution was contributed to the community brain
   */
  contributed?: boolean;

  /**
   * Additional note about the contribution
   */
  contributionNote?: string;
}

// =============================================================================
// Stats Types
// =============================================================================

/**
 * Statistics about the Clawdex knowledge base
 */
export interface ClawdexStats {
  /**
   * Total number of records in the knowledge base
   */
  totalRecords: number;

  /**
   * Number of error fix records
   */
  errorFixes: number;

  /**
   * Number of decision records
   */
  decisions: number;

  /**
   * Number of pattern records
   */
  patterns: number;

  /**
   * Path to the data directory (local storage only)
   */
  dataDirectory?: string;
}

// =============================================================================
// Response Types
// =============================================================================

/**
 * Generic result of logging an operation
 */
export interface LogResult {
  /**
   * Whether the operation was successful
   */
  success: boolean;

  /**
   * Human-readable message about the operation
   */
  message: string;

  /**
   * ID of the created record (if successful)
   */
  recordId?: string;

  /**
   * Whether any secrets were redacted from the input
   */
  secretsRedacted?: boolean;
}

/**
 * Result of getting stats
 */
export interface StatsResult {
  /**
   * Whether the operation was successful
   */
  success: boolean;

  /**
   * Human-readable message
   */
  message: string;

  /**
   * The statistics
   */
  stats: ClawdexStats;
}

// =============================================================================
// API Response Types (Internal)
// =============================================================================

/**
 * Raw API response for error fix logging
 * @internal
 */
export interface ApiLogErrorFixResponse {
  success: boolean;
  record_id?: string;
  message: string;
  secrets_redacted?: boolean;
}

/**
 * Raw API response for decision logging
 * @internal
 */
export interface ApiLogDecisionResponse {
  success: boolean;
  record_id?: string;
  message: string;
}

/**
 * Raw API response for pattern logging
 * @internal
 */
export interface ApiLogPatternResponse {
  success: boolean;
  record_id?: string;
  message: string;
}

/**
 * Raw API response for finding solutions
 * @internal
 */
export interface ApiFindSolutionResponse {
  found: boolean;
  message: string;
  solutions: Array<{
    id: string;
    solution: string;
    original_error: string;
    context: Record<string, string | undefined>;
    confidence: number;
    verified: boolean;
    source: "local" | "community";
  }>;
  suggestion?: string;
}

/**
 * Raw API response for finding decisions
 * @internal
 */
export interface ApiFindDecisionResponse {
  found: boolean;
  message: string;
  decisions: Array<{
    id: string;
    title: string;
    choice: string;
    alternatives?: string[];
    relevance: number;
  }>;
  suggestion?: string;
}

/**
 * Raw API response for finding patterns
 * @internal
 */
export interface ApiFindPatternResponse {
  found: boolean;
  message: string;
  patterns: Array<{
    id: string;
    name: string;
    category: string;
    problem: string;
    solution: string;
    relevance: number;
  }>;
  suggestion?: string;
}

/**
 * Raw API response for verifying a solution
 * @internal
 */
export interface ApiVerifySolutionResponse {
  success: boolean;
  message: string;
  record_id: string;
  verified_as: string;
  contributed?: boolean;
  contribution_note?: string;
}

/**
 * Raw API response for stats
 * @internal
 */
export interface ApiStatsResponse {
  success: boolean;
  message: string;
  stats: {
    total_records: number;
    error_fixes: number;
    decisions: number;
    patterns: number;
    data_directory?: string;
  };
}
