# Perfil Congresso

```js
const deputados = await FileAttachment(
  "data/load_deputados.csv"
).csv({typed: true})

const partidos = [
  "Todos",
  ...Array.from(
    new Set(deputados.map(d => d.siglaPartido))
  ).sort()
]

const sexos = [
  "Todos",
  ...Array.from(
    new Set(deputados.map(d => d.sexo))
  ).sort()
]
```

```js
const partidoSelecionado = view(
  Inputs.select(partidos, {
    label: "Partido",
    value: "Todos"
  })
)
```
```js
const sexoSelecionado = view(
  Inputs.select(sexos, {
    label: "Sexo",
    value: "Todos"
  })
)
```

```js
const deputadosFiltrado = deputados.filter(d => {

  const partidoOk =
    partidoSelecionado === "Todos" ||
    d.siglaPartido === partidoSelecionado;

  const sexoOk =
    sexoSelecionado === "Todos" ||
    d.sexo === sexoSelecionado;

  return partidoOk && sexoOk;
})
```
<!-- Cards with big numbers -->

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Número de deputados</h2>
    <span class="big">${deputadosFiltrado.length.toLocaleString("pt-BR")}</span>
  </div>
</div>

<!-- -------------------------------------------------------------- -->

<!-- -------------------------------------------------------------- -->
## Composição partidária

<!-- GRAFICO PIZZA -->
```js
const composicao_partidos = d3.rollups(
  deputadosFiltrado,
  v => v.length,
  d => d.siglaPartido
).map(([siglaPartido, total]) => ({
  siglaPartido,
  total
}))
```

```js
function partidoTreemap(data, {width} = {}) {

  const height = 420;

  const root = d3.hierarchy({
    name: "Partidos",
    children: data.map(d => ({
      name: d.siglaPartido,
      value: d.total
    }))
  })
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

  d3.treemap()
    .size([width, height])
    .paddingInner(3)
    .round(true)(root);

  const color = d3.scaleOrdinal()
    .domain(data.map(d => d.siglaPartido))
    .range(d3.schemeTableau10);

  const totalDeputados = d3.sum(data, d => d.total);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

  const leaf = svg.selectAll("g")
    .data(root.leaves())
    .join("g")
      .attr(
        "transform",
        d => `translate(${d.x0},${d.y0})`
      );

  /* retângulos */
  leaf.append("rect")
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => color(d.data.name))
    .attr("stroke", "white")
    .attr("stroke-width", 2);

  /* tooltip */
  leaf.append("title")
    .text(d => {

      const pct =
        (100 * d.value / totalDeputados).toFixed(1);

      return `${d.data.name}
${d.value} deputados
${pct}%`;
    });

  /* nome partido */
  leaf.append("text")
    .attr("x", 8)
    .attr("y", 22)
    .style("fill", "white")
    .style("font-size", "16px")
    .style("font-weight", "bold")
    .text(d => d.data.name);

  /* valor absoluto + % */
  leaf.append("text")
    .attr("x", 8)
    .attr("y", 44)
    .style("fill", "white")
    .style("font-size", "13px")
    .text(d => {

      const pct =
        (100 * d.value / totalDeputados).toFixed(1);

      return `${d.value} (${pct}%)`;
    });

  return svg.node();
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => partidoTreemap(composicao_partidos, {width}))}
  </div>
</div>

<!-- -------------------------------------------------------------- -->

<!-- -------------------------------------------------------------- -->
## Distribuição de gênero

<!-- GRAFICO PIZZA -->
```js
const genero = d3.rollups(
  deputadosFiltrado,
  v => v.length,
  d => d.sexo
).map(([sexo, total]) => ({
  sexo,
  total
}))
```

```js
function genderPieChart(data, {width} = {}) {
  const height = 400;
  const radius = Math.min(width, height) / 2;

  const pie = d3.pie().value(d => d.total);
  const arc = d3.arc().innerRadius(0).outerRadius(radius - 20);

  const color = d3.scaleOrdinal()
    .domain(data.map(d => d.sexo))
    .range(d3.schemeCategory10);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height]);

  svg.selectAll("path")
    .data(pie(data))
    .join("path")
      .attr("d", arc)
      .attr("fill", d => color(d.data.sexo))
      .attr("stroke", "white")
      .attr("stroke-width", 2);

  const legend = svg.append("g")
  .attr("transform", `translate(${width / 2 - 74}, ${-height / 2 + 16})`);

  genero.forEach((d, i) => {

    const row = legend.append("g")
      .attr("transform", `translate(0, ${i * 25})`);

    /*retangulos coloridos*/
    row.append("rect")
      .attr("width", 16)
      .attr("height", 16)
      .attr("fill", color(d.sexo));

    /*texto*/
    row.append("text")
      .attr("x", 24)
      .attr("y", 13)
      .style("font-size", "14px")
      .style("fill", "white")
      .text(`${d.sexo}`);
  });

  return svg.node();
}
```

<!-- MAPA -->
```js
const br = await fetch(
  "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
).then(r => r.json());

const generoPorUf = d3.rollups(
  deputadosFiltrado,
  v => ({
    total: v.length,
    mulheres: v.filter(d => d.sexo === "F").length,
    homens: v.filter(d => d.sexo === "M").length
  }),
  d => d.siglaUf
).map(([siglaUf, values]) => ({
  siglaUf,
  ...values
}));

const generoRelativoPorUf = d3.rollups(
  deputadosFiltrado,
  v => {
    const total = v.length;
    const mulheres = v.filter(d => d.sexo === "F").length;

    return {
      total,
      mulheres,
      pct_mulheres: mulheres *100 / total
    };
  },
  d => d.siglaUf
).map(([siglaUf, values]) => ({
  siglaUf,
  ...values
}));
```

```js
function mapaUFs(data, {width} = {}) {

  const values = new Map(
    data.map(d => [d.siglaUf, d.mulheres])
  );

  return Plot.plot({
    title: "Mulheres parlamentares por UF",

    width,
    height: 300,

    projection: {
      type: "mercator",
      domain: br
    },

    color: {
      type: "linear",
      scheme: "Purples",
      label: "Número de mulheres",
      legend: true
    },

    marks: [
      Plot.geo(br, {
        fill: d => values.get(d.properties.sigla) ?? 0,
        stroke: "white",
        strokeWidth: 1,
        tip: true
      })
    ]
  });
}
```

```js
function mapaUFs_mulheres_rel(data, {width} = {}) {

  const values = new Map(
    data.map(d => [d.siglaUf, d.pct_mulheres])
  );

  return Plot.plot({
    title: "Número relativo de mulheres deputadas, por UF",

    width,
    height: 300,

    projection: {
      type: "mercator",
      domain: br
    },

    color: {
      type: "linear",
      scheme: "Purples",
      label: "% de mulheres",
      legend: true
    },

    marks: [
      Plot.geo(br, {
        fill: d => values.get(d.properties.sigla) ?? 0,
        stroke: "white",
        strokeWidth: 1,
        tip: true
      })
    ]
  });
}
```

<!-- EXIBIR -->
<div class="grid grid-cols-2">
  <div class="card">
    <h2>Número de deputados homens</h2>
    <span class="big">${deputadosFiltrado.filter((d) => d.sexo === "M").length.toLocaleString("pt-BR")}</span>
  </div>
  <div class="card">
    <h2>Número de deputadas mulheres</h2>
    <span class="big">${deputadosFiltrado.filter((d) => d.sexo === "F").length.toLocaleString("pt-BR")}</span>
  </div>
</div>

<div class="grid grid-cols-3">
  <div class="card">
    ${resize((width) => genderPieChart(genero, {width}))}
  </div>
  <div class="card">
    ${resize((width) => mapaUFs(generoPorUf, {width}))}
  </div>
  <div class="card">
    ${resize((width) => mapaUFs_mulheres_rel(generoRelativoPorUf, {width}))}
  </div>
</div>

<!-- ------------------------------------------------------------------------------------------------- -->

<!-- ------------------------------------------------------------------------------------------------- -->
## Cor e raça

TODO

<!-- ------------------------------------------------------------------------------------------------- -->

<!-- ------------------------------------------------------------------------------------------------- -->
## Escolaridade

```js
// PARA GRÁFICO PIZZA
const escolaridadeAggMap = {
  "Doutorado": "Pós-Graduação",
  "Mestrado": "Pós-Graduação",
  "Doutorado Incompleto": "Pós-Graduação Incompleta",
  "Mestrado Incompleto": "Pós-Graduação Incompleta"
};

const escolaridade = d3.rollups(
  deputadosFiltrado,
  v => v.length,
  d => escolaridadeAggMap[d.escolaridade] ?? d.escolaridade
).map(([escolaridade, total]) => ({
  escolaridade,
  total
}));

const escolaridadeScore = {
  "Primário Incompleto": 0,
  "Ensino Fundamental": 1,
  "Ensino Médio Incompleto": 2,
  "Ensino Médio": 3,
  "Superior Incompleto": 4,
  "Superior": 5,
  "Pós-Graduação Incompleta": 6,
  "Pós-Graduação": 7,
  "Mestrado Incompleto": 6,
  "Mestrado": 7,
  "Doutorado Incompleto": 8,
  "Doutorado": 9
}
```

```js
const deputadosComEscolaridadeScore = deputadosFiltrado
  .map(d => ({
    ...d,
    escolaridade_score: escolaridadeScore[d.escolaridade] ?? d.escolaridade
  }))
  .filter(d => d.escolaridade_score != null)

const escolaridadePorUf = d3.rollups(
  deputadosComEscolaridadeScore,
  v => ({
    total: v.length,
    escolaridade_media: d3.mean(v, d => d.escolaridade_score)
  }),
  d => d.siglaUf
).map(([siglaUf, values]) => ({
  siglaUf,
  ...values
}))
```

```js
function escolaridadeTreemap(data, {width} = {}) {
  const height = 420;

  const root = d3.hierarchy({
    name: "Escolaridade",
    children: data.map(d => ({
      name: d.escolaridade,
      value: d.total
    }))
  })
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

  d3.treemap()
    .size([width, height])
    .paddingInner(3)
    .round(true)(root);

  const color = d3.scaleOrdinal()
    .domain(data.map(d => d.escolaridade))
    .range(d3.schemeCategory10);

  const total = d3.sum(data, d => d.total);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

  const leaf = svg.selectAll("g")
    .data(root.leaves())
    .join("g")
      .attr("transform", d => `translate(${d.x0},${d.y0})`);

  leaf.append("rect")
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => color(d.data.name))
    .attr("stroke", "white")
    .attr("stroke-width", 2);

  leaf.append("title")
    .text(d => {
      const pct = (100 * d.value / total).toFixed(1);
      return `${d.data.name}: ${d.value} (${pct}%)`;
    });

  leaf.append("text")
    .attr("x", 8)
    .attr("y", 22)
    .style("fill", "white")
    .style("font-size", "14px")
    .style("font-weight", "bold")
    .text(d => d.data.name);

  leaf.append("text")
    .attr("x", 8)
    .attr("y", 44)
    .style("fill", "white")
    .style("font-size", "12px")
    .text(d => {
      const pct = (100 * d.value / total).toFixed(1);
      return `${d.value} (${pct}%)`;
    });

  return svg.node();
}
```

<!-- MAPA ESCOLARIDADE MÉDIA-->
```js
function mapaEscolaridadeUFs(data, {width} = {}) {
  const values = new Map(
    data.map(d => [d.siglaUf, d.escolaridade_media])
  );

  return Plot.plot({
    title: "Escolaridade média dos deputados por UF",

    width,
    height: 300,

    projection: {
      type: "mercator",
      domain: br
    },

    color: {
      type: "linear",
      scheme: "Blues",
      label: "Escolaridade média",
      legend: true
    },

    marks: [
      Plot.geo(br, {
        fill: d => values.get(d.properties.sigla) ?? null,
        stroke: "white",
        strokeWidth: 1,
        tip: true
      })
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => escolaridadeTreemap(escolaridade, {width}))}
  </div>
    <div class="card">
    ${resize((width) => mapaEscolaridadeUFs(escolaridadePorUf, {width}))}
  </div>
</div>

<!-- ------------------------------------------------------------------------------------------------- -->

<!-- ------------------------------------------------------------------------------------------------- -->
## Distribuição etária

```js
const deputadosVivos = deputadosFiltrado.filter(
  d => !d.dataFalecimento
)

const anoAtual = new Date().getFullYear();

const idades = deputadosVivos.map(d => ({
  idade:
    anoAtual -
    new Date(d.dataNascimento).getFullYear()
}))
```

<!-- HISTOGRAMA ABSOLUTO -->
```js
function histogramaIdades(data, {width} = {}) {

  return Plot.plot({
    title: "Número de deputados por faixa etária",

    width,
    height: 300,

    y: {
      grid: true,
      label: "Contagem"
    },

    x: {
      label: "Idade (anos)"
    },

    marks: [
      Plot.rectY(
        data,
        Plot.binX(
          {y: "count"},
          {
            x: "idade",
            thresholds: d3.range(20, 101, 10),
            fill: "#4F46E5",
            tip: true
          }
        )
      ),

      Plot.ruleY([0])
    ]
  });
}
```
<!-- HISTOGRAMA PERCENTUAL -->
```js
function histogramaIdadesPct(data, {width} = {}) {

  return Plot.plot({
    title: "Distribuição percentual por faixa etária",

    width,
    height: 300,

    y: {
      grid: true,
      label: "% dos deputados",
      percent: true
    },

    x: {
      label: "Idade (anos)"
    },

    marks: [
      Plot.rectY(
        data,
        Plot.binX(
          {y: d => d.length / data.length},
          {
            x: "idade",
            thresholds: d3.range(20, 101, 10),
            fill: "#059669",
            tip: true
          }
        )
      ),

      Plot.ruleY([0])
    ]
  });
}
```

<!--  EXIBIR -->
<div class="grid grid-cols-2">

  <div class="card">
    ${resize((width) =>
      histogramaIdades(idades, {width})
    )}
  </div>

  <div class="card">
    ${resize((width) =>
      histogramaIdadesPct(idades, {width})
    )}
  </div>

</div>