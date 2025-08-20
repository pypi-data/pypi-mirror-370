import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'


const container = document.getElementById('cosmograph-root')

const graphData = {
  nodes: JSON.parse(container.dataset.nodes || "[]"),
  links: JSON.parse(container.dataset.links || "[]"),
}
const params = JSON.parse(container.getAttribute("params") || "{}")
const legend = JSON.parse(container.getAttribute("legend") || "{}")
ReactDOM.createRoot(container).render(<App data={graphData}  params={params} legend={legend}/>)
