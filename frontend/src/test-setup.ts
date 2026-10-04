import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";

// Sem `globals`, o Testing Library nao desmonta os componentes sozinho entre testes. Um hook que
// registra listener no document (ex: atalhos de teclado) continuaria vivo no teste seguinte e
// interceptaria eventos que nao sao dele.
afterEach(() => cleanup());

// O jsdom nao implementa a rolagem da janela (so loga "Not implemented"). Troca por espioes, que
// tambem deixam os testes conferirem se a pagina foi rolada.
beforeEach(() => {
  Object.defineProperty(window, "scrollTo", { value: vi.fn(), writable: true, configurable: true });
  Object.defineProperty(window, "scrollBy", { value: vi.fn(), writable: true, configurable: true });
});
