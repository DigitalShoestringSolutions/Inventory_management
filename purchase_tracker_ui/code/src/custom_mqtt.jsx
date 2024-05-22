import * as dayjs from 'dayjs'

export async function custom_new_message_action(dispatch, message) {
  // console.log(message)
  if (message && message.topic.match("order_db/state/update")) {
    dispatch({ type: 'ITEM_UPDATE', update: message.payload })
  } else if (message && message.topic.match("order_db/state/changed")) {
    dispatch({ type: 'BULK_CHANGED', changed_set: message.payload })
  } else if (message && message.topic.match("order_db/state/new")) {
    dispatch({ type: 'BULK_NEW', new_set: message.payload })
  }
  // } else if (message && message.topic.match("location_state/entered")) {
  //   dispatch({ type: 'ITEM_ENTERED', added_entry: message.payload })
  // } else if (message && message.topic.match("location_state/exited")) {
  //   dispatch({ type: 'ITEM_EXITED', removed_entry: message.payload })
  // }
}

export const CustomReducer = (currentState, action) => {
  console.log(action)
  // let filtered_items_state = []
  // let new_item_history = []
  switch (action.type) {
    case 'MQTT_STATUS':
      return {
        ...currentState,
        connected: action.connected
      };
    case 'SUB_STATE':
      return {
        ...currentState,
        subbed: action.subbed
      };
    case 'SET_ITEMS':
      return {
        ...currentState,
        items: action.items
      }
    case 'ITEM_UPDATE':
      let new_state = currentState.items.map((elem) => {
        if (elem.id === action.update.id) {
          let output = { ...elem }
          output.state = action.update.state
          action.update.items.forEach(item_update => {
            let item_entry = output.items.find(item => item.id === item_update.id)
            if (item_entry)
              item_entry.complete = item_update.complete
            else
              console.error("warning: item " + item_update + " not found during update")
          })
          return output
        } else {
          return elem
        }
      })
      return {
        ...currentState,
        items: new_state
      }
    case 'SET_FROM_DATE':
      return {
        ...currentState,
        from_date: action.value.isValid() ? action.value : dayjs()
      }
    case 'SET_TO_DATE':
      return {
        ...currentState,
        to_date: action.value.isValid() ? action.value : currentState.from_date.add(1, "day")
      }
    case 'SET_FROM_SLOT':
      return {
        ...currentState,
        from_slot: action.value
      }
    case 'SET_TO_SLOT':
      return {
        ...currentState,
        to_slot: action.value
      }
    case 'BULK_CHANGED':
      let changed_ids = action.changed_set.map(elem => elem.id)
      let unchanged = currentState.items.filter(elem => !changed_ids.includes(elem.id))
      return {
        ...currentState,
        items: [...unchanged, ...action.changed_set]
      }
    case 'BULK_NEW':
        return {
          ...currentState,
          items: [...currentState.items, ...action.new_set]
        }
    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
};
