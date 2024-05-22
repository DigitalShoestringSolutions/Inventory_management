
import APIBackend from './RestAPI'

export const load_config = async (setPending, setLoaded, setError, setConfig) => {
  setPending(true)
  APIBackend.api_get('http://' + document.location.host + '/config/config.json').then((response) => {
    const get_json = async (response) => {
      let output = await response.json()
      return { status: response.status, payload: output }
    }
    return get_json(response)
  }).then((response) => {
    if (response.status === 200) {
      const raw_conf = response.payload;
      console.log("config", raw_conf)
      setConfig(raw_conf)
      setLoaded(true)
    } else {
      console.log("ERROR LOADING CONFIG")
      setError("ERROR: Unable to load configuration!")
    }
  }).catch((err) => {
    console.error(err.message);
    setError("ERROR: Unable to load configuration!")
  })
}
