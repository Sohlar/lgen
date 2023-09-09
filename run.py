from app import create_app
import cProfile

app = create_app()

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    app.run(host='0.0.0.0', port=5001, debug=True)
    profiler.disable()
    profiler.print_stats(sort='time') 
    app.run(host='0.0.0.0', port=5001, debug=True)
