function ShowFunctions(props) {
  return (
    <div className="card text-center">
      <div className="card-body">
        <h5 className="card-title">{props.funcName}</h5>
        <p className="card-text">{props.funcDescription}.</p>
        <button 
          type="button" 
          className="btn btn-primary" 
          onClick={props.onClick}
        >
          Select
        </button>
      </div>
    </div>
  );
}

export default ShowFunctions;
