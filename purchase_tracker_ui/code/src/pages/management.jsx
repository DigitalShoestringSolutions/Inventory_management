import { Card, Table, Button, Form } from "react-bootstrap";
import { set_state_active, set_state_complete, set_item_complete } from '../fetch_data'
import React from "react";
import { groupBy } from '../table_utils'
import { useMQTTDispatch, useMQTTState } from "../MQTTContext";
import { DISPLAY_STATE } from "../constants";
import { useToastDispatch, add_toast } from "../ToastContext";
import { OrdersPage } from "./orders";


export function ManagementPage(props) {
    let { config, display_state } = props
    let [item_pending, setItemPending] = React.useState(false)
    let [item_error, setItemError] = React.useState(false)
    let [item_complete, setItemComplete] = React.useState(false)
    let toast_dispatch = useToastDispatch()

    let dispatch = useMQTTDispatch();
    let { items } = useMQTTState();

    const updateItem = (payload) => {
        dispatch({ type: "ITEM_UPDATE", update: payload })
        add_toast(toast_dispatch, { header: "Update", body: ("Order " + payload.order_number + " set to " + payload.state) })
    }

    const acknowledge_action = {
        label: "Acknowledge",
        style: "secondary",
        callback: (id) => set_state_active(config, id, setItemPending, setItemComplete, setItemError, updateItem)
    }

    const complete_action = {
        label: "Complete",
        style: "success",
        callback: (id) => set_state_complete(config, id, setItemPending, setItemComplete, setItemError, updateItem)
    }

    const incomplete_action = {
        label: "Incomplete",
        style: "danger",
        callback: (id) => set_state_active(config, id, setItemPending, setItemComplete, setItemError, updateItem)
    }

    let item_status = { item_pending, item_error, item_complete }

    let grouped = groupBy(items, "state")
    return <>
        <Section title={"New:"} data={grouped.new} action={acknowledge_action} item_status={item_status} {...props} />
        <Section title={"Changed:"} data={grouped.changed} action={acknowledge_action} item_status={item_status} {...props} />
        <Section title={"Active:"} data={grouped.active} action={complete_action} item_status={item_status} {...props} />
        <Section title={"Complete:"} data={grouped.complete} action={incomplete_action} item_status={item_status} {...props} />
    </>
}

function Section({ title, data = [], action, item_status, config, display_state, header_offset }) {
    let widths = {
        order_number: "5%",
        customer: "15%",
        date: "10%",
        slot: "10%",
        notes: "50%",
        button: "10%"
    }

    if (display_state === DISPLAY_STATE.minimised) {
        widths = {
            order_number: "10%",
            customer: "30%",
            date: "15%",
            slot: "15%",
            notes: "20%",
            button: "10%"
        }
    }

    return <Card className='my-2'>
        <Card.Header className='d-flex flex-row justify-content-between bg-body sticky-top' style={{ top: header_offset }}>
            <h3 className='flex-shrink-0 flex-grow-1 m-0'>{title}</h3>
        </Card.Header>
        <Card.Body className="p-0">
            {data.length > 0 ?
                <Table bordered striped responsive>
                    <colgroup>
                        <col span="1" style={{ width: widths.order_number }} />
                        <col span="1" style={{ width: widths.customer }} />
                        <col span="1" style={{ width: widths.date }} />
                        <col span="1" style={{ width: widths.slot }} />
                        <col span="1" style={{ width: widths.notes }} />
                        <col span="1" style={{ width: widths.button }} />
                    </colgroup>
                    <thead>
                        <tr>
                            {["Order Number", "Customer", "Date", "Delivery", "Items", ""].map((column, index) => (
                                <th key={index}>{column}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, index) => (
                            <TableRow key={index} config={config} entry={row} action={action} item_status={item_status} display_state={display_state} />
                        ))}
                    </tbody>
                </Table>
                : "None"}
        </Card.Body>
    </Card>

}

function TableRow({ entry, action, item_status, config, display_state }) {
    return <tr>
        <td>{entry.order_number}</td>
        <td>{entry.customer}</td>
        <td>{entry.delivery_date}</td>
        <td>{entry.delivery_slot}</td>
        <td className={display_state === DISPLAY_STATE.detailed ? "p-0" : "p-1"}>
            <ItemList config={config} items={entry.items} display_state={display_state} />
        </td>
        <td className="p-1">
            <Button size="sm" variant={action.style} onClick={() => (action.callback(entry.id))}>{action.label} </Button>
        </td>
    </tr>
}

function ItemList(props) {
    let { display_state, items } = props

    let incomplete = items.filter(elem => elem.complete === false)

    switch (display_state) {
        case DISPLAY_STATE.minimised:
            return (incomplete ? incomplete.length : 0) + "/" + items.length + " item(s) remaining"
        case DISPLAY_STATE.condensed:
            return <ItemListCondensed {...props} />
        case DISPLAY_STATE.detailed:
            return <ItemListTable {...props} />
        default:
            return "invalid display format"
    }
}

function ItemListCondensed({ config, items }) {
    let total = items.length - 1
    return <div className="p-0 m-0">
        {items.map((item, index) => (
            <span key={item.id} className={item.complete ? "text-decoration-line-through" : ""}>
                <Quantity quantity={item.quantity} unit={item.unit} /> {item.description}{index !== total ? " | " : ""}
            </span>
        ))}
    </div>
}

function Quantity({ quantity, unit }) {
    if (unit === "kg")
        return quantity + " kg"
    else if (unit === "ca")
        return quantity + " x cartons"
    else
        return quantity + "x"
}

function ItemListTable({ config, items }) {
    let [loaded, setLoaded] = React.useState(false)
    let [pending, setPending] = React.useState(false)
    let [error, setError] = React.useState(null)

    let dispatch = useMQTTDispatch()

    return <Table borderless size="sm" className="p-0 m-0">
        <colgroup>
            <col span="1" style={{ width: "10%" }} />
            <col span="1" style={{ width: "10%" }} />
            <col span="1" style={{ width: "70%" }} />
            <col span="1" style={{ width: "10%" }} />
        </colgroup>
        <tbody>
            {items.map(item => (
                <React.Fragment key={item.id}>
                    <tr>
                        <td>{item.quantity}</td>
                        <td>{item.unit}</td>
                        <td>{item.description}</td>
                        <td><Form.Check checked={item.complete} onChange={(evt) => set_item_complete(config, item.id, evt.target.checked, setPending, setLoaded, setError, (payload) => dispatch({ type: "ITEM_UPDATE", update: payload }))} /></td>
                    </tr>
                    {item.notes
                        ? <tr><td colSpan={4} className="table-info px-2">{" "}{item.notes}</td></tr> : ""}
                </React.Fragment>
            ))}
        </tbody>
    </Table>
}
