import React from "react";
import { Badge, Button, Col, Form, InputGroup, Row, Table, Spinner, Card, Accordion } from "react-bootstrap";
import { groupBy } from "../table_utils";


export function AddItemsPanel({
    selected_items, 
    setSelectedItems,
    item_list,
    selected_title,
    selected_fields,
    available_title,
    available_fields,
    map_on_select = [],
    group_header_label = (first_entry) => "undefined",
    group_key = undefined,
}) {
    let available_items = item_list ? item_list.filter(elem => Object.keys(selected_items).indexOf(String(elem.id)) === -1) : []

    if (item_list == undefined)
        return

    const select_item = (item) => {
        setSelectedItems(prev => {
            let entry = item_list.find(elem => elem.id === item)
            let new_entry = { ...entry}
            map_on_select.forEach(mapping => {
                if(mapping.from)
                    new_entry[mapping.to] = new_entry[mapping.from]
                else if(mapping.value !== undefined)
                    new_entry[mapping.to] = mapping.value
            })
            return {
                ...prev,
                [item]: new_entry
            }
        })
    }

    const unselect_item = (item) => {
        setSelectedItems(prev => {
            const { [item]: removed, ...rest } = prev;
            return rest;
        })
    }

    const set_field = (value, field, id) => {
        setSelectedItems(prev => ({ ...prev, [id]: { ...prev[id], [field]: value } }))
    }

    return <Row className="mt-2">
        <Col>
            <Card>
                <Card.Header className="mb-0">{selected_title}</Card.Header>
                <Card.Body className="p-1">
                    <SelectedItemList
                        selected_items={selected_items}
                        set_field={set_field}
                        unselect_item={unselect_item}
                        fields={selected_fields}
                    />
                </Card.Body>
            </Card>
        </Col>
        <Col>
            <Card>
                <Card.Header className="mb-0">{available_title}</Card.Header>
                <Card.Body className="p-1">
                    {group_key ?
                        <AvailableItemsAccordian
                            available_items={available_items}
                            select_item={select_item}
                            fields={available_fields}
                            group_key={group_key}
                            group_header_label={group_header_label}
                        />
                        :
                        <AvailableItemsList available_items={available_items} select_item={select_item} fields={available_fields} />
                    }
                </Card.Body>
            </Card>
        </Col>
    </Row>
}

function AvailableItemsList({ available_items, select_item, fields }) {
    return <Table bordered size="sm" className="mb-0">
        <thead>
            <tr>
                {fields.map(elem => <th key={elem.key}>{elem.label}</th>)}
            </tr>
        </thead>
        <tbody>
            {available_items.map(elem => <tr key={elem.id}>
                <AvailableItemElement elem={elem} fields={fields} on_click={() => select_item(elem.id)} />
            </tr>)}
        </tbody>
    </Table>
}

function AvailableItemsAccordian({ available_items, select_item, group_key, group_header_label, fields }) {
    let grouped_items = groupBy(available_items, group_key)
    let groups = Object.keys(grouped_items)
    return <div className="border">
        <Accordion flush={true} alwaysOpen={true}>
            {groups.map(entry => (
                <Accordion.Item key={entry} eventKey={entry}>
                    <Accordion.Header>{group_header_label(grouped_items[entry][0])}</Accordion.Header>
                    <Accordion.Body className="p-0">
                        <Table bordered size="sm" className="mb-0">
                            <thead>
                                <tr>
                                    {fields.map(elem => <th key={elem.key}>{elem.label}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {grouped_items[entry].map((elem, index) => <tr key={elem.id}>
                                    <AvailableItemElement elem={elem} fields={fields} on_click={() => select_item(elem.id)} />
                                </tr>)}
                            </tbody>
                        </Table>
                    </Accordion.Body>
                </Accordion.Item>
            ))}
        </Accordion>
    </div>
}

function get_nested(obj,nested_key){
    let key_fragments = nested_key.split('.')
    var tmp = obj
    while (key_fragments.length>0){
        let fragment = key_fragments.shift()
        tmp = tmp[fragment]
    }
    return tmp
}

function AvailableItemElement({ elem, fields, on_click }) {
    return <>
        {fields.map(field => (
            field.key !== "$select$"
                ? <td key={field.key}>{get_nested(elem,field.key)}</td>
                : <td key={field.key} className="p-0 py-0"><Button size="sm" variant="outline-primary" className="w-100 h-100 rounded-0" onClick={on_click}>Select</Button></td>
        ))}
    </>
}

function SelectedItemList({ selected_items, set_field, unselect_item, fields }) {
    return <Table bordered size="sm" className="mb-0">
        <thead>
            <tr>
                {fields.map(elem => <th key={elem.key}>{elem.label}</th>)}
            </tr>
        </thead>
        <tbody>
            {Object.keys(selected_items).map(id =>
                <SelectedItemElement
                    key={id}
                    elem={selected_items[id]}
                    set_field={(value, field) => set_field(value, field, id)}
                    on_click={() => unselect_item(id)}
                    fields={fields}
                />
            )}
        </tbody>
    </Table>
}

function SelectedItemElement({ elem, set_field, on_click, fields }) {
    return <tr>
        {fields.map(field => {
            if (field.key === "$unselect$")
                return <td key={field.key} className="p-0 py-1">
                    <Button size="sm" className="w-100 h-100 rounded-0" variant="outline-danger" onClick={on_click}>
                        Unselect
                    </Button>
                </td>
            if (field.key.charAt(0) === '#') {
                let input_field_key = field.key.substring(1)
                return <td key={field.key} className="p-1" >
                    <Form.Control
                        size="sm"
                        className="w-100 h-100 rounded-0"
                        onChange={(event) => set_field(event.target.value.replace(/\D/gm, "")??"", input_field_key)}
                        value={elem[input_field_key]??""} />
                </td >
            } else
                return <td key={field.key}>{get_nested(elem, field.key)}</td>
        })}
    </tr>
}