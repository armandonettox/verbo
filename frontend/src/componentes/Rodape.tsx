const URL_LICENCA = 'https://github.com/armandonettox/verbo/blob/master/LICENSE'

// Autoria e licenca, como no app antigo (aparecia so na tela inicial)
export function Rodape() {
  return (
    <footer className="rodape">
      <p>
        Feito por{' '}
        <a href="https://armandonetto.com/" target="_blank" rel="noopener noreferrer">
          Armando Netto
        </a>
      </p>
      <p>
        Protegido sob{' '}
        <a href={URL_LICENCA} target="_blank" rel="noopener noreferrer">
          Licenca Verbo 1.0
        </a>
      </p>
    </footer>
  )
}
