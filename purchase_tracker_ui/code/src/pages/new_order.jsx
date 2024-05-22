import React from "react";
import { Form, Card, Button, Alert, Container, Spinner, Row, Col, Table, Accordion, InputGroup, OverlayTrigger, Tooltip } from "react-bootstrap";
import { useMutation, useQuery } from "react-query"
import APIBackend from '../RestAPI'
import * as dayjs from 'dayjs'
import { useNavigate } from "react-router-dom";

import { AddItemsPanel } from '../components/add_item_panel'
import { NewSupplierModal } from "./new_supplier";
import { SuppliedItemsModal } from "./supplied_items";

const get_url = (config) => ((config.db.host ? config.db.host : window.location.hostname) + (config.db.port ? ":" + config.db.port : ""))

/*
    PO number
    Ordered by
    supplier
    
    date_enquired - can be blank
    date_order_placed - auto today
    date_expected_delivery

    items:
        item
        quantity
*/


export function NewOrderPage({ config }) {
    let navigate = useNavigate()
    let [purchase_order_reference, setPurchaseOrder] = React.useState("")
    let [ordered_by, setOrderedBy] = React.useState("")
    let [supplier, setSupplier] = React.useState("")

    let [date_order_placed, setDateOrderPlaced] = React.useState(dayjs())
    let [date_expected_delivery, setDateExpectedDelivery] = React.useState(dayjs())

    let [selected_items, setSelectedItems] = React.useState({})

    let [validated, setValidated] = React.useState(false)
    let [errors, setErrors] = React.useState({})

    let [just_created, setJustCreated] = React.useState({ id: undefined, name: undefined })

    let [new_supplier_modal, setNewSupplierModal] = React.useState(false)
    let [supplied_item_modal, setSuppliedItemModal] = React.useState(false)

    let url = get_url(config)
    const { isLoading, error, data: suppliers } = useQuery(
        ['supplier_list'],
        () =>
            fetch('http://' + url + '/api/supplier/').then(res =>
                res.json()
            )
    )

    const { isLoading: supplier_loading, error: supplier_errro, data: supplier_details } = useQuery(
        ['supplied_item', supplier],
        () =>
            fetch('http://' + url + '/api/supplier/' + supplier+'/').then(res =>
                res.json()
            ),
        {
            // The query will not execute until the supplier exists
            enabled: !!supplier,
        }
    )

    const create_mutation = useMutation(
        async (data) => {
            let url = "http://" + get_url(config) + "/api/order/"
            console.log(url)
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
                console.log(result)
                if (result.status !== 201) {
                    setValidated(true)
                    setErrors(result.payload)
                } else {
                    setValidated(false)
                    setErrors({})
                    setPurchaseOrder("")
                    setOrderedBy("")
                    setSupplier("")
                    setDateExpectedDelivery(dayjs())
                    setDateOrderPlaced(dayjs())
                    setJustCreated(result.payload)
                }
            }
        }
    )


    let handleSubmit = (evt) => {
        evt.preventDefault();
        create_mutation.mutate({
            supplier: supplier,
            ordered_by: ordered_by,
            purchase_order_reference: purchase_order_reference,
            date_order_placed: date_order_placed.format("YYYY-MM-DD"),
            date_expected_delivery: date_expected_delivery.format("YYYY-MM-DD"),
            items: Object.keys(selected_items).map(key => ({ item: selected_items[key].item.id, quantity_requested: selected_items[key].quantity }))
        })
    }
    return <Container fluid="sm">
        <Card className="mt-3">
            <Card.Header>
                <div className="d-flex flex-row align-items-baseline justify-content-between flex-wrap">
                    <h2>New Order</h2>
                    <Button
                        variant="outline-secondary"
                        className="bi bi-arrow-left"
                        onClick={() => navigate("/")}
                    >{" "}Back</Button>
                </div>
            </Card.Header>
            <Card.Body>
                <Form noValidate validated={validated} onSubmit={handleSubmit} className="mb-3">
                    <Form.Group className="mb-3">
                        <Form.Label>Supplier</Form.Label>
                        {suppliers ?
                            <InputGroup>
                                <Form.Select value={supplier} onChange={event => setSupplier(event.target.value)} disabled={create_mutation.isPending}>
                                    <option hidden disabled value={""}>Select a supplier</option>
                                    {suppliers.map(entry => (
                                        <option key={entry.id} value={entry.id}>{entry.name}</option>
                                    ))}
                                </Form.Select>
                                <OverlayTrigger overlay={<Tooltip>Add a new Supplier</Tooltip>}>
                                    <Button variant="outline-primary" onClick={() => setNewSupplierModal(true)}>New</Button>
                                </OverlayTrigger>
                            </InputGroup>
                            : <Spinner size="sm" />}
                        <Form.Label>Purchase Order</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="<Enter purchase order number here>"
                            value={purchase_order_reference}
                            onChange={(event) => setPurchaseOrder(event.target.value)}
                            disabled={create_mutation.isPending}
                            isInvalid={'purchase_order_reference' in errors}
                            required
                        />
                        <Form.Control.Feedback type="invalid">{errors?.purchase_order_reference}</Form.Control.Feedback>
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Ordered By</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="<Enter your name here>"
                            value={ordered_by}
                            onChange={(event) => setOrderedBy(event.target.value)}
                            disabled={create_mutation.isPending}
                            isInvalid={'ordered_by' in errors}
                            required
                        />
                        <Form.Control.Feedback type="invalid">{errors?.ordered_by}</Form.Control.Feedback>
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Order Placed</Form.Label>
                        <Form.Control type="date" placeholder="" value={date_order_placed.format("YYYY-MM-DD")} onChange={(event) => setDateOrderPlaced(dayjs(event.target.value))} disabled={create_mutation.isPending} />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Expected Delivery</Form.Label>
                        <Form.Control type="date" placeholder="" value={date_expected_delivery.format("YYYY-MM-DD")} onChange={(event) => setDateExpectedDelivery(dayjs(event.target.value))} disabled={create_mutation.isPending} />
                    </Form.Group>
                    <AddItemsPanel
                        selected_items={selected_items}
                        setSelectedItems={setSelectedItems}
                        item_list={supplier_details?.supplied_items}
                        available_title={<div className="d-flex flex-row align-items-baseline justify-content-between flex-wrap">
                            <span>Available from Supplier</span>
                            <Button variant="outline-primary" size="sm" onClick={() => setSuppliedItemModal(true)}>Edit Supplied Items</Button>
                        </div>}
                        available_fields={[
                            { key: "item.name", label: "Item" },
                            { key: "expected_lead_time", label: "Lead Time" },
                            { key: "$select$", label: "Add to Order" }
                        ]}
                        selected_title="Items in Order"
                        selected_fields={[
                            { key: "item.name", label: "Item" },
                            { key: "expected_lead_time", label: "Lead Time" },
                            { key: "#quantity", label: "Quantity" },
                            { key: "$unselect$", label: "Remove from Order" }
                        ]}
                        map_on_select={
                            [
                                {
                                    value: 0,
                                    to: "quantity"
                                }
                            ]
                        }
                    />
                    <div className="d-grid mt-2">
                        <Button type="submit" disabled={create_mutation.isPending}>Save</Button>
                    </div>
                </Form>

                {create_mutation.isError ? (
                    <Alert variant="danger">An error occurred: {create_mutation.error.message}</Alert>
                ) : null}

                {create_mutation.isSuccess ?
                    (just_created.id ?
                        <Alert variant="success" className="d-flex align-items-baseline justify-content-between">
                            <span>Order created.</span>
                            <Button variant="success" onClick={() => navigate('/')}>Back to Order List</Button>
                        </Alert>
                        : <Alert variant="warning" className="d-flex align-items-baseline justify-content-between">Please fill out the required fields.</Alert>)
                    : null
                }
            </Card.Body>
        </Card>
        <NewSupplierModal
            show={new_supplier_modal}
            onHide={(new_supplier_id = undefined) => {
                setNewSupplierModal(false)
                if (new_supplier_id)
                    setSupplier(new_supplier_id)
            }}
            config={config} />

        <SuppliedItemsModal
            show={supplied_item_modal}
            onHide={() => setSuppliedItemModal(false)}
            config={config}
            supplier={supplier}
        />
    </Container>
}















