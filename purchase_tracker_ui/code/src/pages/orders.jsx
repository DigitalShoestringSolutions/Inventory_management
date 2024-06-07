import { useMQTTState } from "../MQTTContext";
import { groupBy } from '../table_utils'
import { DISPLAY_STATE } from "../constants";
import { Card, Table, Badge } from "react-bootstrap";
import React from 'react';

export function OrdersPage(props) {
    let { items } = useMQTTState();

    let date_grouped = groupBy(items, "delivery_date")
    let slot_grouped = Object.keys(date_grouped).reduce((acc, key) => { acc[key] = groupBy(date_grouped[key], "delivery_slot"); return acc }, {})

    return <>
        {Object.keys(slot_grouped).map(delivery_date => <React.Fragment key={delivery_date}>
            <Group {...props} title={delivery_date + " (AM)"} data={slot_grouped[delivery_date]?.AM} />
            <Group {...props} title={delivery_date + " (PM)"} data={slot_grouped[delivery_date]?.PM} />
        </React.Fragment>)}
    </>
}

function Group({ title, data = [], display_state, header_offset}) {
    let widths = {
        order_number: "5%",
        customer: "15%",
        date: "10%",
        slot: "10%",
        notes: "50%"
    }

    if (display_state === DISPLAY_STATE.minimised) {
        widths = {
            order_number: "10%",
            customer: "30%",
            date: "15%",
            slot: "15%",
            notes: "20%",
        }
    }

    let incomplete = data.filter(elem => elem.state !== "complete")
    let remaining_orders = incomplete.length

    if (data.length > 0) {
        return <Card className='my-2'>
            <Card.Header className="py-1 px-2 sticky-top bg-body border-bottom d-flex flex-row align-items-baseline justify-content-between" style={{ top: header_offset }}>
                <h3 className='flex-shrink-0 flex-grow-1 m-0'>{title}</h3> <h3><Badge bg="secondary">{remaining_orders} Remaining</Badge></h3>
            </Card.Header>
            <Card.Body className="p-0">
                {incomplete.length > 0 ?
                    <Table bordered striped responsive>
                        <colgroup>
                            <col span="1" style={{ width: widths.order_number }} />
                            <col span="1" style={{ width: widths.customer }} />
                            <col span="1" style={{ width: widths.notes }} />
                        </colgroup>
                        <thead>
                            <tr>
                                {["Order Number", "Customer", "Items"].map((column, index) => (
                                    <th key={index}>{column}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {incomplete.map((row, index) => (
                                <TableRow key={index} entry={row} display_state={display_state} />
                            ))}
                        </tbody>
                    </Table>
                    : "None"}
            </Card.Body>
        </Card>
    }
}

function TableRow({ entry, display_state }) {
    let colour = ""
    if (entry.state === "new"){
        colour = "table-success"
    } else if (entry.state === "changed"){
        colour = "table-warning"
    }
    return <tr>
        <td className={colour}>{entry.order_number}</td>
        <td className={colour}>{entry.customer}</td>
        <td className={display_state === DISPLAY_STATE.detailed ? "p-0" : "p-1"}>
            <ItemList items={entry.items} display_state={display_state} />
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
            return <ItemListCondensed {...props} items={incomplete} />
        case DISPLAY_STATE.detailed:
            return <ItemListTable {...props} items={incomplete} />
        default:
            return "invalid display format"
    }
}

function ItemListCondensed({ items }) {
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

function ItemListTable({ items }) {
    return <Table borderless size="sm" className="p-0 m-0">
        <colgroup>
            <col span="1" style={{ width: "10%" }} />
            <col span="1" style={{ width: "10%" }} />
            <col span="1" style={{ width: "80%" }} />
        </colgroup>
        <tbody>
            {items.map(item => (
                <React.Fragment key={item.id}>
                    <tr>
                        <td>{item.quantity}</td>
                        <td>{item.unit}</td>
                        <td>{item.description}</td>
                    </tr>
                    {item.notes
                        ? <tr><td colSpan={4} className="table-info px-2">{" "}{item.notes}</td></tr> : ""}
                </React.Fragment>
            ))}
        </tbody>
    </Table>
}