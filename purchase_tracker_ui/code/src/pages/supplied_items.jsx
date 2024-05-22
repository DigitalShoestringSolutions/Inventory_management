import React from "react";
import { Form, Modal, Button, Alert, Container } from "react-bootstrap";
import { useMutation, useQueryClient, useQuery } from "react-query"
import APIBackend from '../RestAPI'
import { AddItemsPanel } from "../components/add_item_panel";
import { NewItemModal } from "./new_item_modal";


const get_url = (config) => ((config.db.host ? config.db.host : window.location.hostname) + (config.db.port ? ":" + config.db.port : ""))

export function SuppliedItemsModal({ config, show, onHide, supplier }) {
    const queryClient = useQueryClient()
    let [new_item_modal,setNewItemModal] = React.useState(false)
    let [selected_items, setSelectedItems] = React.useState({})


    const { data: supplier_details } = useQuery(
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
    let [errors, setErrors] = React.useState({})

    React.useEffect(() => {
        if (supplier_details) {
            setSelectedItems(supplier_details.supplied_items.reduce((obj, entry) => {
                obj[entry.item.id] = {
                    id: entry.item.id,
                    name: entry.item.name,
                    expected_lead_time: entry.expected_lead_time,
                    product_page: entry.product_page,
                }
                return obj
            }, {}))
        }
    }, [supplier_details])

    let url = get_url(config)
    const { isLoading, error, data: known_items } = useQuery(
        ['known_items'],
        () =>
            fetch('http://' + url + '/api/known_items/').then(res =>
                res.json()
            )
    )

    const add_supplied_items_mutation = useMutation(
        async (data) => {
            let url = "http://" + get_url(config) + "/api/supplier/" + supplier + "/update_supplied_items/"
            console.log(url)
            return APIBackend.api_put(url, data).then((response) => {
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
                if (result.status === 200) {
                    queryClient.invalidateQueries({ queryKey: ['supplied_item', supplier] })
                } else {
                    setErrors(result.payload)
                }
            }
        }
    )


    React.useEffect(() => {
        if (!show)
            add_supplied_items_mutation.reset()
    }, [show])

    let do_save = () => {
        add_supplied_items_mutation.mutate(Object.keys(selected_items).map(key => ({
            item: selected_items[key].id,
            expected_lead_time: selected_items[key].expected_lead_time,
        })))
    }

    return <Modal show={show} fullscreen={true} onHide={onHide}>
        <Modal.Header closeButton>Add Supplied Items</Modal.Header>
        <Modal.Body>
            <AddItemsPanel
                selected_items={selected_items}
                setSelectedItems={setSelectedItems}
                item_list={known_items}
                available_title={<div className="d-flex flex-row align-items-baseline justify-content-between flex-wrap">
                    <span>All Items</span>
                    <Button variant="outline-primary" size="sm" onClick={() => setNewItemModal(true)}>Add New Item</Button>
                </div>}
                available_fields={[
                    { key: "name", label: "Item" },
                    { key: "$select$", label: "Add to Supplier" }
                ]}
                selected_title="Provided by Supplier"
                selected_fields={[
                    { key: "name", label: "Item" },
                    { key: "#expected_lead_time", label: "Lead Time (days)" },
                    // { key: "#quantity", label: "Quantity" },
                    { key: "$unselect$", label: "Remove from Supplier" }
                ]}
                map_on_select={
                    [
                        {
                            value: "",
                            to: "expected_lead_time"
                        }
                    ]
                }
            />
            <div className="d-grid mt-2">
                <Button onClick={do_save} disabled={add_supplied_items_mutation.isPending}>Save</Button>
            </div>

            {add_supplied_items_mutation.isError ? (
                <Alert variant="danger">An error occurred: {add_supplied_items_mutation.error.message}</Alert>
            ) : null}

            {Object.keys(errors).length > 0 ? (
                <Alert variant="danger">Errors Occured: {JSON.stringify(errors)}</Alert>
            ) : null}

            {add_supplied_items_mutation.isSuccess && Object.keys(errors).length === 0 ?
                <Alert variant="success" className="d-flex align-items-baseline justify-content-between"><span>Supplied Items Saved</span>
                    <Button size="sm" variant="success" onClick={() => onHide()}>Close</Button></Alert>
                : null}
        </Modal.Body>
        <NewItemModal config={config} show={new_item_modal} onHide={() => setNewItemModal(false)} />
    </Modal>
}