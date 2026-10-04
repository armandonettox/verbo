import ReactMarkdown from 'react-markdown'

// O texto vem de um modelo de IA: o react-markdown nao interpreta HTML cru,
// entao so a marcacao markdown vira elemento
export function Markdown({ texto }: { texto: string }) {
  return (
    <div className="markdown">
      <ReactMarkdown
        components={{
          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {texto}
      </ReactMarkdown>
    </div>
  )
}
