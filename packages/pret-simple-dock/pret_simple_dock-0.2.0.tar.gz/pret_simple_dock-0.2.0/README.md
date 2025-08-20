# React-Simple-Dock

A set of React components to create a dockable interface, allowing to arrange and resize tabs.

## Installation of the javascript package

```bash
npm install react-simple-dock
```

## Installation of the PRET python package

```bash
pip install pret-simple-dock
```

## Demo

[![Edit react-simple-dock](https://codesandbox.io/static/img/play-codesandbox.svg)](https://codesandbox.io/p/sandbox/zwgwp3)

## Usage

```tsx
import React from "react";
import ReactDOM from "react-dom";
import { Layout, Panel } from "react-simple-dock";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

const DEFAULT_CONFIG = {
    kind: "row",
    size: 100,
    children: [
        {
            kind: "column",
            size: 50,
            children: [
                { kind: "leaf", tabs: ["Panel 1"], tabIndex: 0, size: 50 },
                { kind: "leaf", tabs: ["Panel 2"], tabIndex: 0, size: 50 },
            ],
        },
        { kind: "leaf", tabs: ["Panel 3"], tabIndex: 0, size: 50 },
    ],
};

const App = () => (
    <div style={{ background: "#bdbdbd", width: "100vw", height: "100vh" }}>
        <Layout
            /* optional initial layout config */
            defaultConfig={DEFAULT_CONFIG}
        >
            <Panel key="Panel 1">
                <p>Content 1</p>
            </Panel>
            <Panel key="Panel 2" header={<i>Italic title</i>}>
                <p>Content 2</p>
            </Panel>
            <Panel key="Panel 3">
                <p>Content 3</p>
            </Panel>
        </Layout>
    </div>
);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(<App />);
```

## Development

### Installation

Clone the repository:

```bash
git clone https://github.com/percevalw/react-simple-dock.git
cd react-simple-dock
```

Install the dependencies:

```bash
yarn install
```

Make your changes and run the demo:

```bash
yarn start
```

### Build the javascript library

To build the javascript library:

```bash
yarn build:lib
```

### Build the PRET python package

Ensure `pret` is installed.

```bash
pip install pret
```

If you have changed the signature of the components, you will need to update the python stubs.

```bash
pret stub . SimpleDock pret/ui/simple_dock/__init__.py
```

To build the python library and make it available in your environment:

```bash
pip install .
```
