export const initialState = {
  next_id: 0,
  toasts: {},
  pending: []
};

export const ToastReducer = (currentState, action) => {
  console.log(action)
  switch (action.type) {
    case "ADD_TOAST":
      //add to pending
      if (Object.keys(currentState.toasts).length > 3) {
        return {
          ...currentState,
          next_id: currentState.next_id + 1,
          pending: [...currentState.pending, { id: currentState.next_id, toast: action.new_toast }]
        }
      } else { //add to active
        return {
          ...currentState,
          next_id: currentState.next_id + 1,
          toasts: { ...currentState.toasts, [currentState.next_id]: action.new_toast }
        };
      }
    case "REMOVE_TOAST":
      let new_toasts = Object.keys(currentState.toasts).reduce((acc, key) => {
        if (key !== action.remove_key) {
          acc[key] = currentState.toasts[key]
        }
        return acc
      }, {})
      let new_pending = currentState.pending

      if(currentState.pending.length > 0){
        let next_toast = new_pending.shift()
        new_toasts[next_toast.id] = next_toast.toast
      }

      return {
        ...currentState,
        toasts: new_toasts,
        pending: new_pending,
      };

    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
};