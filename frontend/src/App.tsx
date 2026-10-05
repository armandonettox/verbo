import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Raiz } from './componentes/Raiz.tsx'
import { BuscaProvider } from './contexto/BuscaProvider.tsx'
import { Home } from './paginas/Home.tsx'
import { Leitura } from './paginas/Leitura.tsx'

export default function App() {
  return (
    <BrowserRouter>
      <BuscaProvider>
        <Routes>
          <Route element={<Raiz />}>
            <Route path="/" element={<Home />} />
            <Route path="/buscar" element={<Home />} />
            <Route path="/ler/:livro/:capitulo" element={<Leitura />} />
          </Route>
        </Routes>
      </BuscaProvider>
    </BrowserRouter>
  )
}
