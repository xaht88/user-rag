"use client";

import type { LlmConfig, ViewState } from "../shared/types";

interface LLMSelectorProps {
  config: LlmConfig;
  state?: ViewState;
  onChange: (nextConfig: LlmConfig) => void;
}

export function LLMSelector({ config, state = "success", onChange }: LLMSelectorProps) {
  const disabled = state === "loading";

  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2">
      <label className="text-sm font-medium text-slate-700" htmlFor="provider">
        LLM
      </label>
      <select
        id="provider"
        className="rounded-md border border-slate-300 px-2 py-1 text-sm"
        disabled={disabled}
        value={config.provider}
        onChange={(event) => onChange({ provider: event.target.value as LlmConfig["provider"], model: config.model })}
      >
        <option value="openai">OpenAI</option>
        <option value="ollama">Ollama</option>
      </select>
      <select
        className="rounded-md border border-slate-300 px-2 py-1 text-sm"
        disabled={disabled}
        value={config.model}
        onChange={(event) => onChange({ provider: config.provider, model: event.target.value })}
      >
        {config.provider === "openai" ? (
          <>
            <option value="gpt-4o-mini">gpt-4o-mini</option>
            <option value="gpt-4o">gpt-4o</option>
          </>
        ) : (
          <>
            <option value="llama3.1">llama3.1</option>
            <option value="mistral">mistral</option>
          </>
        )}
      </select>
      {state === "error" ? <span className="text-xs text-red-600">Провайдер недоступен</span> : null}
    </div>
  );
}
