import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import { LLMSelector } from "./llm-selector";

describe("LLMSelector", () => {
  test("вызывает onChange при смене модели", () => {
    const onChange = vi.fn();
    render(
      <LLMSelector
        config={{ provider: "openai", model: "gpt-4o-mini" }}
        onChange={onChange}
      />
    );

    const modelSelect = screen.getAllByRole("combobox")[1];
    fireEvent.change(modelSelect, { target: { value: "gpt-4o" } });

    expect(onChange).toHaveBeenCalledWith({ provider: "openai", model: "gpt-4o" });
  });
});
