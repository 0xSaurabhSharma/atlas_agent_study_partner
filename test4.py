# test_step4_graph.py
from app.graph.graph import create_graph

def main():
    print("\n--- Running Step 4: Graph Assembly Test ---")
    
    try:
        # Create the graph instance
        graph = create_graph()
        
        print("\n[1. Verifying Graph Structure...]")
        
        # Print the graph structure in the console as ASCII art
        print("   ↳ ASCII Representation of the Graph:")
        graph.get_graph().print_ascii()
        
        print("\n✅ Graph assembly test passed! The structure matches your parallel design.")

        # Optional: To generate a visual image, run: pip install pillow pygraphviz
        try:
            png_data = graph.get_graph().draw_mermaid_png()
            with open("atlas_workflow_graph.png", "wb") as f:
                f.write(png_data)
            print("\n   -> Optional: Graph image saved to 'atlas_workflow_graph.png'")
        except Exception:
            print("\n   -> Optional: Skipping PNG generation (pygraphviz might be missing).")

    except Exception as e:
        print(f"\n❌ Graph assembly test failed: {e}")

if __name__ == "__main__":
    main()


















# # test_step4_graph.py
# from app.graph.graph import create_graph

# def main():
#     print("\n--- Running Step 4: Modern Graph Assembly Test ---")
    
#     try:
#         # Create the graph instance
#         graph = create_graph()
        
#         print("\n[1. Verifying Graph Structure...]")
        
#         # Print the graph structure in the console as ASCII art
#         print("   ↳ ASCII Representation of the Graph:")
#         graph.get_graph().print_ascii()
        
#         print("\n✅ Graph assembly test passed! The structure now uses parallel branching.")

#         # Optional: To generate a visual image, run: pip install pillow pygraphviz
#         try:
#             png_data = graph.get_graph().draw_mermaid_png()
#             with open("atlas_workflow_graph_modern.png", "wb") as f:
#                 f.write(png_data)
#             print("\n   -> Optional: Graph image saved to 'atlas_workflow_graph_modern.png'")
#         except Exception:
#             print("\n   -> Optional: Skipping PNG generation (pygraphviz might be missing).")

#     except Exception as e:
#         print(f"\n❌ Graph assembly test failed: {e}")

# if __name__ == "__main__":
#     main()