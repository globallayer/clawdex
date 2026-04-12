/**
 * Clawdex TypeScript SDK - Custom Error Classes
 *
 * Provides specific error types for different failure scenarios.
 * All errors extend ClawdexError for easy catching.
 *
 * @module clawdex/errors
 */

/**
 * Base error class for all Clawdex SDK errors.
 * Extends the native Error class with additional context.
 */
export class ClawdexError extends Error {
  /**
   * The original error that caused this error, if any
   */
  public readonly cause?: Error;

  /**
   * Additional context about the error
   */
  public readonly context?: Record<string, unknown>;

  constructor(
    message: string,
    options?: { cause?: Error; context?: Record<string, unknown> }
  ) {
    super(message);
    this.name = "ClawdexError";
    this.cause = options?.cause;
    this.context = options?.context;

    // Maintains proper stack trace for where error was thrown (V8 engines)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Returns a JSON representation of the error
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      message: this.message,
      cause: this.cause?.message,
      context: this.context,
      stack: this.stack,
    };
  }
}

/**
 * Error thrown when there's a network or connection issue.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.findSolution({ errorMessage: "..." });
 * } catch (error) {
 *   if (error instanceof NetworkError) {
 *     console.log("Network issue:", error.message);
 *     // Maybe retry or use cached data
 *   }
 * }
 * ```
 */
export class NetworkError extends ClawdexError {
  /**
   * The HTTP status code, if available
   */
  public readonly statusCode?: number;

  /**
   * The URL that failed
   */
  public readonly url?: string;

  constructor(
    message: string,
    options?: {
      cause?: Error;
      statusCode?: number;
      url?: string;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "NetworkError";
    this.statusCode = options?.statusCode;
    this.url = options?.url;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      statusCode: this.statusCode,
      url: this.url,
    };
  }
}

/**
 * Error thrown when the API returns an error response.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.logErrorFix({ errorMessage: "", solution: "" });
 * } catch (error) {
 *   if (error instanceof ApiError) {
 *     console.log("API error:", error.statusCode, error.body);
 *   }
 * }
 * ```
 */
export class ApiError extends ClawdexError {
  /**
   * The HTTP status code
   */
  public readonly statusCode: number;

  /**
   * The response body, if available
   */
  public readonly body?: unknown;

  /**
   * The request URL
   */
  public readonly url?: string;

  /**
   * The request method
   */
  public readonly method?: string;

  constructor(
    message: string,
    statusCode: number,
    options?: {
      body?: unknown;
      url?: string;
      method?: string;
      cause?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.body = options?.body;
    this.url = options?.url;
    this.method = options?.method;
  }

  /**
   * Returns true if this is a client error (4xx)
   */
  isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  /**
   * Returns true if this is a server error (5xx)
   */
  isServerError(): boolean {
    return this.statusCode >= 500 && this.statusCode < 600;
  }

  /**
   * Returns true if the error might be resolved by retrying
   */
  isRetryable(): boolean {
    // Retry on server errors and specific client errors
    return (
      this.statusCode >= 500 ||
      this.statusCode === 408 || // Request Timeout
      this.statusCode === 429 // Too Many Requests
    );
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      statusCode: this.statusCode,
      body: this.body,
      url: this.url,
      method: this.method,
    };
  }
}

/**
 * Error thrown when the API request times out.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.findSolution({ errorMessage: "...", limit: 100 });
 * } catch (error) {
 *   if (error instanceof TimeoutError) {
 *     console.log("Request timed out after", error.timeout, "ms");
 *   }
 * }
 * ```
 */
export class TimeoutError extends ClawdexError {
  /**
   * The timeout duration in milliseconds
   */
  public readonly timeout: number;

  /**
   * The URL that timed out
   */
  public readonly url?: string;

  constructor(
    message: string,
    timeout: number,
    options?: {
      url?: string;
      cause?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "TimeoutError";
    this.timeout = timeout;
    this.url = options?.url;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      timeout: this.timeout,
      url: this.url,
    };
  }
}

/**
 * Error thrown when input validation fails.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.logErrorFix({ errorMessage: "", solution: "" });
 * } catch (error) {
 *   if (error instanceof ValidationError) {
 *     console.log("Invalid input:", error.field, error.message);
 *   }
 * }
 * ```
 */
export class ValidationError extends ClawdexError {
  /**
   * The field that failed validation
   */
  public readonly field?: string;

  /**
   * The value that failed validation
   */
  public readonly value?: unknown;

  /**
   * The validation rule that failed
   */
  public readonly rule?: string;

  constructor(
    message: string,
    options?: {
      field?: string;
      value?: unknown;
      rule?: string;
      cause?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "ValidationError";
    this.field = options?.field;
    this.value = options?.value;
    this.rule = options?.rule;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      field: this.field,
      value: this.value,
      rule: this.rule,
    };
  }
}

/**
 * Error thrown when authentication fails.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.findSolution({ errorMessage: "..." });
 * } catch (error) {
 *   if (error instanceof AuthenticationError) {
 *     console.log("Invalid API key");
 *   }
 * }
 * ```
 */
export class AuthenticationError extends ClawdexError {
  constructor(
    message: string = "Authentication failed",
    options?: { cause?: Error; context?: Record<string, unknown> }
  ) {
    super(message, options);
    this.name = "AuthenticationError";
  }
}

/**
 * Error thrown when rate limit is exceeded.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.findSolution({ errorMessage: "..." });
 * } catch (error) {
 *   if (error instanceof RateLimitError) {
 *     console.log("Rate limited. Retry after:", error.retryAfter, "seconds");
 *   }
 * }
 * ```
 */
export class RateLimitError extends ClawdexError {
  /**
   * Number of seconds to wait before retrying
   */
  public readonly retryAfter?: number;

  /**
   * The rate limit that was exceeded
   */
  public readonly limit?: number;

  /**
   * Current usage count
   */
  public readonly current?: number;

  constructor(
    message: string = "Rate limit exceeded",
    options?: {
      retryAfter?: number;
      limit?: number;
      current?: number;
      cause?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "RateLimitError";
    this.retryAfter = options?.retryAfter;
    this.limit = options?.limit;
    this.current = options?.current;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      retryAfter: this.retryAfter,
      limit: this.limit,
      current: this.current,
    };
  }
}

/**
 * Error thrown when a requested resource is not found.
 *
 * @example
 * ```typescript
 * try {
 *   await clawdex.verifySolution({ id: "invalid-id", success: true });
 * } catch (error) {
 *   if (error instanceof NotFoundError) {
 *     console.log("Record not found:", error.resourceId);
 *   }
 * }
 * ```
 */
export class NotFoundError extends ClawdexError {
  /**
   * The type of resource that wasn't found
   */
  public readonly resourceType?: string;

  /**
   * The ID of the resource that wasn't found
   */
  public readonly resourceId?: string;

  constructor(
    message: string = "Resource not found",
    options?: {
      resourceType?: string;
      resourceId?: string;
      cause?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, { cause: options?.cause, context: options?.context });
    this.name = "NotFoundError";
    this.resourceType = options?.resourceType;
    this.resourceId = options?.resourceId;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      resourceType: this.resourceType,
      resourceId: this.resourceId,
    };
  }
}
