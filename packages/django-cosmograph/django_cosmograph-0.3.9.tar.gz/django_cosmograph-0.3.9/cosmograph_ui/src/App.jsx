import { useEffect,useMemo, useState, useRef } from 'react'
import { Cosmograph,CosmographProvider } from '@cosmograph/react'

function Legend({ legend, toggleGroup }) {
  const legendBoxStyle = {
    position: 'absolute',
    top: '5rem',
    right: '2.5rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    padding: '1rem',
    borderRadius: '0.25rem',
    fontSize: '0.875rem',
    zIndex: 10
  };
  const legendDotStyle = {
    top: '5rem',
    right: '2.5rem',
    padding: '0.5rem',
    borderRadius: '1rem',
    fontSize: '0.75rem',
    zIndex: 10,
    marginRight: '0.5rem',
  }

  return (
    <div style={legendBoxStyle} >
      {legend.map(({ group, colour, selected }) => (
        <div key={group} style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
          <input
            type="checkbox"
            checked={selected}
            onChange={() => toggleGroup(group)}
            style={{ marginRight: 8 }}
          />

          <span style={{
            ...legendDotStyle,
            backgroundColor: colour
          }} ></span>
          <span>{group} {selected}</span>
        </div>
      ))}
    </div>
  );
}


export default function App({ data,params, legend:initialLegend }) {
  const cosmographRef = useRef(null)
  const graphRef = useRef(null);
  const [legend, setLegend] = useState(
  initialLegend.map(item => ({ ...item, selected: item.selected ?? true }))
);
  const selectedGroups = Object.fromEntries(
    legend.map(({ group, selected }) => [group, selected])
  );
  useEffect(() => {
    graphRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const colourMap = Object.fromEntries(legend.map(({ group, colour }) => [group, colour]));
  const {
    backgroundColor = "transparent",
    linkArrows = false,
    scaleNodesOnZoom = false,
    simulationGravity = 0.25,
    simulationRepulsion = 0.1,
    simulationRepulsionTheta = 1.7,
    simulationLinkDistance = 2,
    simulationFriction = 0.85,
    simulationCenter = 0.0,
    renderLinks = true,
    simulationDecay = 1000,
    simulationRepulsionFromMouse = 2.0,
    simulationLinkSpring = 1.0
  } = params || {};

  const graphNodeMap = useMemo(
    () => Object.fromEntries(data.nodes.map(n => [n.id, n])),
    [data.nodes]
  );
  const filteredGraph = useMemo(
    () => ({
      nodes: data.nodes.filter(
        node => selectedGroups[node.group]
      ),
      links: data.links.filter(
        link =>
        selectedGroups[graphNodeMap[link.source].group] &&
          selectedGroups[graphNodeMap[link.target].group]
      ),
    }),
    [data.nodes, data.links, graphNodeMap, selectedGroups]
  );

  const toggleGroup = (group) => {
    setLegend(legend.map(item =>
      item.group === group ? { ...item, selected: !item.selected } : item
    ));
  };

  const playPause = () => {
    if ((cosmographRef.current)?.isSimulationRunning) {
      (cosmographRef.current)?.pause();
    } else {
      (cosmographRef.current)?.start();
    }
  }
  const fitView = () => {
    (cosmographRef.current)?.fitView();
    graphRef.current?.scrollIntoView({ behavior: 'smooth' });
  }

  // Styles
  const controlsStyle = {
    position: 'absolute',
    top: '1.25rem',
    left: 0,
    marginLeft: '1.25rem',
    marginRight: '1.25rem',
    marginTop: '5rem',
    marginBottom: '5rem',
    display: 'flex',
    gap: '0.5rem',
    zIndex: 10
  };

  const controlButtonStyle = {
    paddingLeft: '1rem',
    paddingRight: '1rem',
    paddingTop: '0.25rem',
    paddingBottom: '0.25rem',
    backgroundColor: '#f9fafb',
    border: '1px solid #d1d5db',
    color: '#1f2937',
    borderRadius: '0.25rem',
    transition: 'background-color 0.2s'
  };

  return (
    <div ref={graphRef}>
      <CosmographProvider>
        <Legend legend={legend} toggleGroup={toggleGroup} />
        <Cosmograph
          ref={cosmographRef}
          backgroundColor={backgroundColor}
          nodes={filteredGraph.nodes}
          links={filteredGraph.links}
          linkArrows={linkArrows}
          renderLinks={renderLinks}
          nodeColor={(d) =>  colourMap[d.group] ?? "blue"}
          nodeSize={(d) => d.size ?? 5}
          scaleNodesOnZoom={scaleNodesOnZoom}
          nodeLabelColor={(d) =>  colourMap[d.group] ?? "blue"}
          nodeLabelAccessor={(d) => d.label}
          simulationGravity={simulationGravity}
          simulationRepulsion={simulationRepulsion}
          simulationRepulsionTheta={simulationRepulsionTheta}
          simulationLinkDistance={simulationLinkDistance}
          simulationLinkSpring={simulationLinkSpring}
          simulationFriction={simulationFriction}
          simulationDecay={simulationDecay}
          simulationCenter={simulationCenter}
          simulationRepulsionFromMouse={simulationRepulsionFromMouse}
        />
        <div style={controlsStyle}>
          <button
            onClick={playPause}
            style={controlButtonStyle}
          >
            Pause/Play
          </button>
          <button
            onClick={fitView}
            style={controlButtonStyle}
          >
            Fit
          </button>
        </div>
      </CosmographProvider>
    </div>
  )
}
