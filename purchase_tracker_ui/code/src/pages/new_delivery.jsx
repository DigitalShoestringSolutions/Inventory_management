import React from "react";
import { Badge, Button, Col, Form, InputGroup, Row, Table, Spinner, Alert, Accordion, Card } from "react-bootstrap";
import { useQuery, useMutation } from 'react-query'
import { groupBy } from "../table_utils";
import APIBackend from '../RestAPI'
import { AddItemsPanel } from '../components/add_item_panel'
import { useNavigate } from "react-router-dom";

const get_url = (config) => ((config.db.host ? config.db.host : window.location.hostname) + (config.db.port ? ":" + config.db.port : ""))

export function NewDeliveryPage({ config }) {
    let [supplier, setSupplier] = React.useState(undefined)
    let [selected_items, setSelectedItems] = React.useState({})
    let [errors, setErrors] = React.useState({})
    let navigate = useNavigate()

    let url = get_url(config)
    const searchParams = new URLSearchParams();
    searchParams.append("supplier", supplier)
    searchParams.append("detail", "full")

    const { isLoading, error, data } = useQuery(
        ['available_items', supplier],
        () =>
            fetch('http://' + url + '/api/ordered_item' + "?" + searchParams.toString()).then(res =>
                res.json()
            ),
        {
            // The query will not execute until the supplier exists
            enabled: !!supplier,
        }
    )

    const create_mutation = useMutation(
        async (data) => {
            let url = "http://" + get_url(config) + "/api/delivery/"
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
                    // setValidated(true)
                    // setErrors(result.payload)
                } else {
                    navigate('/')
                    // setValidated(false)
                    // setErrors({})
                    // setPurchaseOrder("")
                    // setOrderedBy("")
                    // setSupplier("")
                    // setDateExpectedDelivery(dayjs())
                    // setDateOrderPlaced(dayjs())
                    // setJustCreated(result.payload)
                }
            }
        }
    )


    let handleSubmit = () => {
        create_mutation.mutate(Object.keys(selected_items).map(key => ({
            ordered_item: key,
            quantity_delivered: selected_items[key].quantity
        })))
    }

    return <Card className="mt-3">
        <Card.Header>
            <div className="d-flex flex-row align-items-baseline justify-content-between flex-wrap">
                <h2>New Delivery</h2>
                <Button
                    variant="outline-secondary"
                    className="bi bi-arrow-left"
                    onClick={() => navigate("/")}
                >{" "}Back</Button>
            </div>
        </Card.Header>
        <Card.Body>
            <DeliveryDetails setSupplier={setSupplier} config={config} />
            <AddItemsPanel
                selected_items={selected_items}
                setSelectedItems={setSelectedItems}
                item_list={data}
                group_key={"purchase_order"}
                group_header_label={(first_entry) => <span>{first_entry.purchase_order} [{first_entry.expected_delivery}]</span>}
                available_title="Expected from Supplier"
                available_fields={[
                    { key: "item", label: "Item" },
                    { key: "remaining", label: "Remaining" },
                    { key: "$select$", label: "Add to Delivery" }
                ]}
                selected_title="Delivery Contents"
                selected_fields={[
                    { key: "item", label: "Item" },
                    { key: "purchase_order", label: "Purchase Order" },
                    { key: "#quantity", label: "Quantity" },
                    { key: "$unselect$", label: "Remove from Delivery" }
                ]}
                map_on_select={
                    [
                        {
                            from: "remaining",
                            to: "quantity"
                        }
                    ]
                }
            />

            <div className="d-grid mt-2">
                <Button onClick={() => handleSubmit()} disabled={create_mutation.isPending || Object.keys(selected_items).length === 0}>Save</Button>
            </div>


            {create_mutation.isError ? (
                <Alert variant="danger">An error occurred: {create_mutation.error.message}</Alert>
            ) : null}


            {Object.keys(errors).length > 0 ? (
                <Alert variant="danger">Errors Occured: {JSON.stringify(errors)}</Alert>
            ) : null}
        </Card.Body>
    </Card>
}
function DeliveryDetails({ setSupplier, config }) {
    let [locked, setLocked] = React.useState(false)
    let [internal_supplier, setInternalSupplier] = React.useState("")

    let url = get_url(config)
    const searchParams = new URLSearchParams();
    searchParams.append("active", "true")
    const { isLoading, error, data: suppliers } = useQuery(
        ['supplier_list'],
        () =>
            fetch('http://' + url + '/api/supplier/?' + searchParams.toString()).then(res =>
                res.json()
            )
    )

    let on_lock = () => {
        if (internal_supplier !== "") {
            setLocked(true)
            setSupplier(internal_supplier)
        } else
            window.alert("Please select the supplier from the dropdown")
    }

    let on_unlock = () => {
        if (confirm("Do you want to change the supplier - this will clear all delivery details input so far")) {
            setLocked(false)
            setSupplier(undefined)
        }
    }

    if (isLoading)
        return <Alert variant="secondary">Loading Supplier List <Spinner size="sm" /></Alert>

    if (error)
        return <Alert variant="danger">Error: Unable to Load Supplier List</Alert>

    return <div>
        <InputGroup>
            <InputGroup.Text>Supplier</InputGroup.Text>
            <Form.Select value={internal_supplier} onChange={event => setInternalSupplier(event.target.value)} disabled={locked}>
                <option hidden disabled value={""}>Select a supplier</option>
                {suppliers.map(entry => (
                    <option key={entry.id} value={entry.id}>{entry.name}</option>
                ))}
            </Form.Select>
            {locked ?
                <Button variant="outline-danger" onClick={on_unlock}>Change</Button>
                :
                <Button variant="success" onClick={on_lock}>Select</Button>
            }
        </InputGroup>
    </div>
}

function AddItemsPanels({
    order_data,
    selected_title = "Delivery Contents",
    available_title = "Expected Items"
}) {
    let [selected_items, setSelectedItems] = React.useState({})
    let available_items = order_data ? order_data.filter(elem => Object.keys(selected_items).indexOf(String(elem.id)) === -1) : []

    const select_item = (item) => {
        console.log(item)
        setSelectedItems(prev => {
            let entry = order_data.find(elem => elem.id === item)
            return {
                ...prev,
                [item]: { ...entry, quantity: entry.remaining }
            }
        })
    }

    const unselect_item = (item) => {
        setSelectedItems(prev => {
            const { [item]: removed, ...rest } = prev;
            return rest;
        })
    }

    const set_quantity = (id, value) => {
        setSelectedItems(prev => ({ ...prev, [id]: { ...prev[id], quantity: value } }))
    }

    return <Row className="mt-2">
        <Col>
            <div className="mb-1">{selected_title}</div>
            <SelectedItemList selected_items={selected_items} set_quantity={set_quantity} unselect_item={unselect_item} />
        </Col>
        <Col>
            <div className="mb-1">{available_title}</div>
            <AvailableItemsAccordian available_items={available_items} select_item={select_item} />
        </Col>
    </Row>
}

function AvailableItemsList({ available_items, select_item }) {
    let grouped_items = groupBy(available_items, "purchase_order")
    console.log(grouped_items)
    return <Table bordered size="sm">
        <thead>
            <tr>
                <th>Purchase Order</th>
                {/* <th>Expected</th> */}
                <th>Item</th>
                <th>Quantity Outstanding</th>
                <th>Add to Delivery</th>
            </tr>
        </thead>
        <tbody>
            {Object.keys(grouped_items).map(entry => (
                <React.Fragment key={entry}>
                    {grouped_items[entry].map((elem, index) => <tr key={elem.id}>
                        {index == 0 ? <>
                            <td rowSpan={grouped_items[entry].length}>{entry}</td>
                            {/* <td rowSpan={available_items[entry].items.length}>{available_items[entry].date_expected_delivery}</td> */}
                        </> : ""}
                        <AvailableItemElement elem={elem} on_click={() => select_item(elem.id)} />
                    </tr>)}
                </React.Fragment>
            ))}
        </tbody>
    </Table>
}

function AvailableItemsAccordian({ available_items, select_item }) {
    let grouped_items = groupBy(available_items, "purchase_order")
    let groups = Object.keys(grouped_items)
    return <Accordion flush alwaysOpen={true}>
        {groups.map(entry => (
            <Accordion.Item key={entry} eventKey={entry}>
                <Accordion.Header>{entry} [{grouped_items[entry][0].expected_delivery}]</Accordion.Header>
                <Accordion.Body className="p-0">
                    <Table bordered size="sm" flush className="mb-1">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Quantity Outstanding</th>
                                <th>Add to Delivery</th>
                            </tr>
                        </thead>
                        <tbody>
                            {grouped_items[entry].map((elem, index) => <tr key={elem.id}>
                                <AvailableItemElement elem={elem} on_click={() => select_item(elem.id)} />
                            </tr>)}
                        </tbody>
                    </Table>
                </Accordion.Body>
            </Accordion.Item>
        ))}
    </Accordion>
}


function AvailableItemElement({ elem, on_click }) {
    return <>
        <td>{elem.item}</td>
        <td>{elem.remaining}</td>
        <td className="p-0 py-0"><Button size="sm" variant="outline-primary" className="w-100 h-100 rounded-0" onClick={on_click}>Select</Button></td>
    </>
}

function SelectedItemList({ selected_items, set_quantity, unselect_item }) {
    return <Table bordered size="sm">
        <thead>
            <tr>
                <th>Item</th>
                <th>Purchase Order</th>
                <th>Quantity Delivered</th>
                <th>Remove from Delivery</th>
            </tr>
        </thead>
        <tbody>
            {Object.keys(selected_items).map(id =>
                <SelectedItemElement key={id} elem={selected_items[id]} set_quantity={(value) => set_quantity(id, value)} on_click={() => unselect_item(id)} />
            )}
        </tbody>
    </Table>
}

function SelectedItemElement({ elem, set_quantity, on_click }) {
    return <tr>
        <td>{elem.item}</td>
        <td>{elem.purchase_order}</td>
        <td className="p-1"><Form.Control size="sm" className="w-100 h-100 rounded-0" onChange={(event) => set_quantity(event.target.value)} value={elem.quantity} /></td>
        <td className="p-0 py-1"><Button size="sm" className="w-100 h-100 rounded-0" variant="outline-danger" onClick={on_click}>Unselect</Button></td>
    </tr>
}