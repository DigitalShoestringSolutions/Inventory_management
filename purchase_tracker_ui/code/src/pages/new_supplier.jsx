import React from "react";
import { Form, Modal, Button, Alert, Container } from "react-bootstrap";
import { useMutation, useQueryClient } from "react-query"
import APIBackend from '../RestAPI'


const get_url = (config) => ((config.db.host ? config.db.host : window.location.hostname) + (config.db.port ? ":" + config.db.port : ""))

export function NewSupplierModal({ config, show, onHide }) {
    const queryClient = useQueryClient()
    let [name, setName] = React.useState("")
    let [just_created, setJustCreated] = React.useState({ id: undefined, name: undefined })
    let [errors, setErrors] = React.useState({})

    const create_mutation = useMutation(
        async (data) => {
            let url = "http://" + get_url(config) + "/api/supplier/"
            return APIBackend.api_post(url, data).then((response) => {
                const get_json = async (response) => {
                    let output = await response.json()
                    return { status: response.status, payload: output }
                }
                return get_json(response)
            })
        },
        {
            onSuccess: (result) => {
                if (result.status === 201) {
                    queryClient.invalidateQueries({ queryKey: ['supplier_list'] })
                    setName("")
                    setJustCreated(result.payload)
                } else {
                    setErrors(result.payload)
                }
            }
        }
    )

    React.useEffect(() => {
        if (!show)
            create_mutation.reset()
    }, [show])

    let do_save = () => {
        create_mutation.mutate({ name: name })
    }
    return <Modal show={show} onHide={onHide}>
        <Modal.Header closeButton>Create a New Supplier</Modal.Header>
        <Modal.Body>
            <Form className="mb-3">
                <Form.Group className="mb-3">
                    <Form.Label>Supplier Name</Form.Label>
                    <Form.Control type="text" placeholder="" value={name} onChange={(event) => setName(event.target.value)} disabled={create_mutation.isPending} />
                </Form.Group>
                <div className="d-grid">
                    <Button onClick={do_save} disabled={create_mutation.isPending}>Save</Button>
                </div>
            </Form>

            {create_mutation.isError ? (
                <Alert variant="danger">An error occurred: {create_mutation.error.message}</Alert>
            ) : null}


            {Object.keys(errors).length > 0 ? (
                <Alert variant="danger">Errors Occured: {JSON.stringify(errors)}</Alert>
            ) : null}

            {create_mutation.isSuccess && Object.keys(errors).length === 0 ?
                <Alert variant="success" className="d-flex align-items-baseline justify-content-between"><span>Supplier "{just_created.name}" created.</span>
                    <Button size="sm" variant="success" onClick={() => onHide(just_created.id)}>Close</Button></Alert>
                : null}
        </Modal.Body>
    </Modal>
}