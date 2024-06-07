import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-icons/font/bootstrap-icons.css'
import Spinner from 'react-bootstrap/Spinner'
import Card from 'react-bootstrap/Card'
import { Form, InputGroup, ToastContainer, Toast, OverlayTrigger, Tooltip, Button, ButtonGroup } from "react-bootstrap";
import Container from 'react-bootstrap/Container'
import { MQTTProvider, useMQTTState, useMQTTDispatch } from './MQTTContext'
import React from 'react';
import { custom_new_message_action, CustomReducer } from './custom_mqtt';
import { ToastProvider } from './ToastContext'
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'

import {
  QueryClient,
  QueryClientProvider,
} from 'react-query'

import * as dayjs from 'dayjs'
import { load_data } from './fetch_data'
import { DELIVERY_SLOT, DISPLAY_STATE } from "./constants";
import './app.css'

import { NewDeliveryPage } from './pages/new_delivery'
import { NewOrderPage } from './pages/new_order';
import { OverviewPage } from './pages/overview';

// import * as dayjs from 'dayjs'
// import * as duration from 'dayjs/plugin/duration';
// import * as relativeTime from 'dayjs/plugin/relativeTime';
import { load_config } from './fetch_data';

// dayjs.extend(duration);
// dayjs.extend(relativeTime)


// Create a client
const queryClient = new QueryClient()

function App() {
  let [loaded, setLoaded] = React.useState(false)
  let [pending, setPending] = React.useState(false)
  let [error, setError] = React.useState(null)

  let [config, setConfig] = React.useState([])

  let load_config_callback = React.useCallback(load_config, [])

  React.useEffect(() => {
    if (!loaded && !pending) {
      load_config_callback(setPending, setLoaded, setError, setConfig)
    }
  }, [load_config_callback, loaded, pending])

  if (!loaded) {
    return <Container fluid="md">
      <Card className='mt-2 text-center'>
        {error !== null ? <h1>{error}</h1> : <div><Spinner></Spinner> <h2 className='d-inline'>Loading Config</h2></div>}
      </Card>
    </Container>
  } else {
    return (
      <MQTTProvider
        host={config?.mqtt?.host ? config.mqtt.host : document.location.hostname}
        port={config?.mqtt?.port ?? 9001}
        prefix={config?.mqtt?.prefix ?? []}
        subscriptions={[]}
        new_message_action={custom_new_message_action}
        reducer={CustomReducer}
        initial_state={{}}
        debug={true}
      >
        <QueryClientProvider client={queryClient}>
          <ToastProvider position='bottom-end'>
            <BrowserRouter>
              <Routing config={config} />
            </BrowserRouter>
          </ToastProvider>
        </QueryClientProvider>
      </MQTTProvider>
    )
  }
}


function Routing(props) {
  return (
    <Routes>
      <Route path='/' element={<Base {...props}/>}>
        <Route path="/order" element={<NewOrderPage {...props} />} />
        <Route path="/delivery" element={<NewDeliveryPage {...props} />} />
        <Route index element={<OverviewPage {...props} />}></Route>
      </Route>
    </Routes>
  )
}

function Base({ }) {
  return <Container fluid className="p-0 px-2 d-flex flex-column">
    <Container fluid className="flex-grow-1 p-0 mb-5 ">
          <Outlet />
    </Container>
  </Container>
}


export default App;
