import { IChatService } from './IChatService';
import { AnthropicService } from './AnthropicService';

/**
 * Types of available AI service providers
 */
export enum ServiceProvider {
  ANTHROPIC = 'claude',
  GEMINI = 'gemini'
}

/**
 * Factory for creating chat service instances
 */
export class ServiceFactory {
  /**
   * Create a chat service instance based on provider type
   * @param provider The service provider to use
   * @returns An instance of IChatService
   */
  static createService(provider: ServiceProvider): IChatService {
    switch (provider) {
      case ServiceProvider.ANTHROPIC:
        return new AnthropicService();
      case ServiceProvider.GEMINI:
        // Placeholder for future Gemini service
        return new AnthropicService();
      default:
        throw new Error(`Unknown service provider: ${provider}`);
    }
  }
}
