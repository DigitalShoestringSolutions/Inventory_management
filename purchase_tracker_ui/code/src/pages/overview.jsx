import React from "react";
import { Form, Card, Button, Alert, Container, Spinner, Row, Col, Table, ButtonGroup, OverlayTrigger, Tooltip } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "react-query"
import { useNavigate } from "react-router-dom";
import APIBackend from '../RestAPI'

const get_url = (config) => ((config.db.host ? config.db.host : window.location.hostname) + (config.db.port ? ":" + config.db.port : ""))

export function OverviewPage({ config }) {
    const navigate = useNavigate();
    const queryClient = useQueryClient()

    let url = get_url(config)
    const { isLoading, data: orders } = useQuery(
        ['order_list'],
        () =>
            fetch('http://' + url + '/api/order/').then(res =>
                res.json()
            )
    )

    const complete_mutation = useMutation(
        async (order_id) => {
            let url = "http://" + get_url(config) + "/api/order/" + order_id+"/"
            console.log(url)
            return APIBackend.api_patch(url, {complete:true}).then((response) => {
                const get_json = async (response) => {
                    let output = await response.json()
                    return { status: response.status, payload: output }
                }
                return get_json(response)
            })
        },
        {
            onSuccess: (result) => {
                if(result.status === 200)
                    queryClient.invalidateQueries({ queryKey: ['order_list'] })
            }
        }
    )

    const set_complete = (order_id) => {
        complete_mutation.mutate(order_id)
    }

    const on_edit = (order_id) => {

    }

    if (isLoading)
        return <Container fluid="sm"><Alert variant="secondary">Loading<Spinner size="sm"></Spinner></Alert></Container>

    return <Card className="mt-2 rounded-bottom-0">
        <Card.Header className="sticky-top bg-body border-bottom">
            <div className="d-flex flex-row align-items-baseline justify-content-between flex-wrap">
                <h2>Orders</h2>
                <ButtonGroup>
                    <Button
                        variant="outline-primary"
                        className="bi bi-basket"
                        onClick={() => navigate("/order")}
                    >{" "}New Order</Button>
                    <Button
                        variant="outline-primary"
                        className="bi bi-truck"
                        onClick={() => navigate("/delivery")}
                    >{" "}New Delivery</Button>
                </ButtonGroup>
            </div>
        </Card.Header>
        <Card.Body className="p-0">
            <OrderList orders={orders} set_complete={set_complete} on_edit={on_edit}/>
        </Card.Body>
    </Card>
}

function OrderList({ orders, set_complete, on_edit }) {

    let fields = [
        { key: "purchase_order_reference", label: "Purchase Order" },
        { key: "supplier.name", label: "Supplier" },
        { key: "ordered_by", label: "Ordered By" },
        { key: "date_order_placed", label: "Order Date" },
        { key: "date_expected_delivery", label: "Delivery Date" }
    ]
    return <Table bordered size="sm" className="mb-0">
        <thead>
            <tr>
                {fields.map(elem => <th key={elem.key}>{elem.label}</th>)}
                <th>Items</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {orders.map(order =>
                <OrderListItem key={order.id} order={order} fields={fields} set_complete={() => set_complete(order.id)} on_edit={() => on_edit(order.id)} />
            )}
        </tbody>
    </Table>
}


function get_nested(obj, nested_key) {
    let key_fragments = nested_key.split('.')
    var tmp = obj
    while (key_fragments.length > 0) {
        let fragment = key_fragments.shift()
        tmp = tmp[fragment]
    }
    return tmp
}

function OrderListItem({ order, fields, set_complete, on_edit }) {
    return <tr>
        {fields.map(field => <td key={field.key}>{get_nested(order, field.key)}</td>)}
        <td className="p-0"><ItemListTable items={order.items} /></td>
        <td className="p-0 d-grid"><ButtonGroup size="sm" className="" aria-label="First group">
            <OverlayTrigger overlay={<Tooltip>Edit</Tooltip>}>
                <Button onClick={on_edit} variant="outline-secondary" className="bi bi-pencil" />
            </OverlayTrigger>
            <OverlayTrigger overlay={<Tooltip>Set Complete</Tooltip>}>
                <Button onClick={set_complete} variant="outline-success" className="bi bi-check-lg" />
            </OverlayTrigger>
        </ButtonGroup></td>
    </tr>
}


function ItemListTable({ items }) {
    return <Table borderless size="sm" className="p-0 m-0">
        <colgroup>
            <col span="1" style={{ width: "70%" }} />
            <col span="1" style={{ width: "30%" }} />
        </colgroup>
        <tbody>
            {items.map(item => (
                <React.Fragment key={item.id}>
                    <tr className={item.remaining <= 0 ? "table-success" : ""}>
                        <td>{item.item.name}</td>
                        <td>{item.quantity_requested - item.remaining}/{item.quantity_requested}</td>
                    </tr>
                </React.Fragment>
            ))}
        </tbody>
    </Table>
}
